from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.matcher import current_bot
from nonebot.log import logger

from io import BytesIO
import re, asyncio

from httpx import AsyncClient
from .config import config
from .draw import SeparateMsg, draw_pic

USER_SPLIT = re.escape(config.fakepic_user_split)
MSG_SPLIT = config.fakepic_message_split
DEL_FACE = config.fakepic_del_cqface


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


async def handle_message(message: Message) -> dict:
    """提取Message中的各种字段"""
    images = []
    text = ""
    for seg in message:
        msgtype = seg.type
        # 文字
        if msgtype == "text":
            text += seg.data.get("text")
        # @某人
        elif msgtype == "at":
            user_name = await get_user_name(seg.data.get("qq"))
            text += f"@{user_name} "
        # 表情
        elif msgtype == "face":
            text += "" if DEL_FACE else str(seg)
        # 图片
        elif msgtype == "image":
            async with AsyncClient() as cli:
                res = await cli.get(seg.data.get("url"))
                images.append(BytesIO(res.content))
    
    msg_dict = {"text": text, "images": images}
    return msg_dict



async def trans_to_list(msg: Message) -> list:
    """
    将Message对象拆分成列表
        [{"user_id": int, "is_robot": bool, "messages": [{"text": str, "images": [BytesIO]}]}, ...]
    """
    s = USER_SPLIT + str(msg)
    matches = re.findall(rf'{USER_SPLIT}(\d{{5,10}})说', s)
    parts = re.split(rf'{USER_SPLIT}(\d{{5,10}})说', s)
    msg_list = []
    for i in range(1, len(parts), 2):
        user_id = int(matches[i // 2])
        messages = parts[i + 1].split(MSG_SPLIT)
        for j in range(len(messages)):
            messages[j] = await handle_message(Message(messages[j]))
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
    