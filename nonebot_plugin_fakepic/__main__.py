from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.matcher import current_bot
from nonebot.log import logger

from io import BytesIO
import re, asyncio, html

from httpx import AsyncClient
from .config import config
from .draw import SeparateMsg, draw_pic


async def get_user_name(user_id: int) -> str:
    bot = current_bot.get()
    try:
        nick = (await bot.get_stranger_info(user_id=user_id))['nick']
    except:
        try:
            async with AsyncClient() as client:
                res = await client.get(f"https://api.usuuu.com/qq/{user_id}")
                data = res.json()
                nick = data.get("data").get("name")
        except Exception as e:
            logger.error(e)
            nick = "QQ用户"
    return nick


async def handle_CQ(msg: dict) -> dict:
    """处理消息中的CQ码"""
    text = msg['text']
    images = []
    # 图片
    urls = re.findall(r'\[CQ:image,file=.*?url=(.*?)\]', text)
    text = re.sub(r'\[CQ:image,file=.*?url=(.*?)\]', '', text)
    for u in urls:
        async with AsyncClient() as cli:
            res = await cli.get(html.unescape(u))
            images.append(BytesIO(res.content))
    # @某人
    at_id_list = re.findall(r'\[CQ:at,qq=(\d+)\]', text)
    for at_id in at_id_list:
        at_nick = await get_user_name(int(at_id))
        text = re.sub(r'\[CQ:at,qq=\d+\]', f'@{at_nick} ', text, 1)
    # 表情
    if config.fakepic_del_cqface:
        text = re.sub(r'\[CQ:face,id=\d+\]', '', text)
    
    msg['text'] = html.unescape(text)
    msg['images'] = images
    return msg



async def trans_to_list(msg: Message) -> list:
    """
    将Message对象拆分成列表
        [{"user_id": int,"is_robot": bool, "messages": [{"text": str, "images": [BytesIO]}]}, ...]
    """
    user_split = re.escape(config.fakepic_user_split)
    message_split = config.fakepic_message_split
    s = user_split + str(msg)
    matches = re.findall(rf'{user_split}(\d{{5,10}})说', s)
    parts = re.split(rf'{user_split}(\d{{5,10}})说', s)
    msg_list = []
    for i in range(1, len(parts), 2):
        user_id = int(matches[i // 2])
        texts = parts[i + 1].split(message_split)
        messages = [{"text": item, "images": []} for item in texts]
        for m in messages:
            m = await handle_CQ(m)
        is_robot = True if 3889000000 < user_id < 3890000000  else False
        msg_list.append({"user_id": user_id, "is_robot": is_robot, "messages": messages})

    return msg_list



matcher = on_regex(r'^\d{5,10}说', priority=10, block=True)

@matcher.handle()
async def handle(event: MessageEvent):
    msg_list = await trans_to_list(event.get_message())
    sep_list = []   # 对每一条消息创建一个对象进行绘制
    user_info = {}  # 存放已获取到的用户信息，减少api请求频率
    for user in msg_list:
        user_id = str(user['user_id'])
        if user_id not in user_info:
            async with AsyncClient() as client:
                head = await client.get(f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100")
                img_bytes = BytesIO(head.content)
                nick_name = await get_user_name(int(user_id))
                user_info[user_id] = {"head": img_bytes, "nick_name": nick_name}
        else:
            img_bytes = user_info[user_id]['head']
            nick_name = user_info[user_id]['nick_name']

        for m in user['messages']:
            sep_list.append(SeparateMsg(img_bytes, nick_name, user['is_robot'], m['text'], m['images']))
    
    pic = await asyncio.to_thread(draw_pic, sep_list)
    await matcher.send(MessageSegment.image(pic))
    