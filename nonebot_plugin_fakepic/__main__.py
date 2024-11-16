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
NICK_START = re.escape(config.fakepic_nick_start)
NICK_END = re.escape(config.fakepic_nick_end)
MSG_SPLIT = config.fakepic_message_split
DEL_FACE = config.fakepic_del_cqface


class MsgInfo:
    def __init__(self, text: str, images: list[BytesIO]):
        self.text = text
        self.images = images

class User:
    def __init__(self, user_id: int, nick_name: str, is_robot: bool, messages: list[MsgInfo]):
        self.user_id = user_id
        self.nick_name = nick_name
        self.is_robot = is_robot
        self.messages = messages


async def get_user_name(user_id: int) -> str:
    bot = current_bot.get()
    try:
        nick = (await bot.get_stranger_info(user_id=user_id))['nick']
    except Exception as e:
        logger.error(e)
        try:
            async with AsyncClient() as client:
                res = await client.get(f"https://api.usuuu.com/qq/{user_id}")
                data = res.json()
                nick = data.get("data").get("name")
        except Exception as e:
            logger.error(e)
            nick = "QQ用户"
    return nick


async def handle_message(message: Message) -> MsgInfo:
    """提取Message中的各种字段"""
    images: list[BytesIO] = []
    text = ""
    for seg in message:
        msgtype = seg.type
        # 文字
        if msgtype == "text":
            text += seg.data["text"]
        # @某人
        elif msgtype == "at":
            user_name = await get_user_name(seg.data["qq"])
            text += f"@{user_name} "
        # 表情
        elif msgtype == "face":
            text += "" if DEL_FACE else str(seg)
        # 图片
        elif msgtype == "image":
            async with AsyncClient() as cli:
                res = await cli.get(seg.data["url"])
                images.append(BytesIO(res.content))
    
    msg = MsgInfo(text, images)
    return msg



async def trans_to_list(msg: Message) -> list[User]:
    """
    将输入Message对象拆分成对应的列表
    """
    s = USER_SPLIT + msg.extract_plain_text()
    pattern = rf'{USER_SPLIT}(\d{{5,10}})({NICK_START}.*?{NICK_END})?说'
    matches = re.findall(pattern, s)
    parts = re.split(pattern, s)
    users: list[User] = []
    for i in range(1, len(parts), 3):
        user_id, nick_name = matches[i // 3]
        user_id = int(user_id)
        messages = parts[i + 2].split(MSG_SPLIT)
        messages = [await handle_message(Message(msg)) for msg in messages]
        is_robot = True if 3889000000 < user_id < 3890000000  else False
        users.append(User(user_id, nick_name[1:-1], is_robot, messages))

    return users



matcher = on_regex(rf'^\d{{5,10}}({NICK_START}.*?{NICK_END})?说', priority=10, block=True)

@matcher.handle()
async def handle(event: MessageEvent):
    users = await trans_to_list(event.get_message())
    sep_list: list[SeparateMsg] = []   # 对每一条消息创建一个对象进行绘制
    users_info: dict[int, dict] = {}  # 存放已获取到的用户信息，减少api请求频率
    for user in users:
        user_id = user.user_id
        if user_id not in users_info:
            async with AsyncClient() as client:
                resp = await client.get(f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100") # 头像
                head_image = BytesIO(resp.content)
                if not user.nick_name:  # 昵称
                    nick_name = await get_user_name(user_id)
                else:
                    nick_name = user.nick_name
                users_info[user_id] = {"head": head_image, "nick_name": nick_name}
        else:
            head_image = users_info[user_id]['head']
            nick_name = users_info[user_id]['nick_name']

        for m in user.messages:
            sep_list.append(SeparateMsg(head_image, nick_name, user.is_robot, m.text, m.images))
    
    pic = await asyncio.to_thread(draw_pic, sep_list)
    await matcher.send(MessageSegment.image(pic))
    