from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.log import logger
from io import BytesIO
import re, asyncio, html

from pathlib import Path
res_path = Path(__file__).parent / "resourse"
FONT = res_path / "arial.ttf"
BOT = res_path / "bot_icon.png"
LEVEL = res_path / "level_icon.png"


from pil_utils import Text2Image, BuildImage
from httpx import AsyncClient
from .config import config

class SeparateMsg:
    def __init__(
            self,
            head: BytesIO,
            nick_name: str,
            is_robot: bool,
            text: str,
            images: list[BytesIO],
    ) -> None:
        self.head = head
        self.nick_name = nick_name
        self.is_robot = is_robot
        self.text = Text2Image.from_text(text, 32, spacing=16, fontname=FONT)
        self.images = images

    background: BuildImage
    current_height: int


    def _handel_pictures(self) -> tuple[int, int, list[BuildImage]]:
        max_size = 600 if self.is_only_one_picture else 300
        width_list = []
        pictures = []
        total_height = 0
        for img in self.images:
            pic = BuildImage.open(img)
            aspect_ratio = pic.width / pic.height
            if aspect_ratio >= 1:
                width = max_size
                height = int(width / aspect_ratio)
            else:
                height = max_size
                width = int(height * aspect_ratio)
            width_list.append(width)
            total_height += height + 10
            pic = pic.resize((width, height)).circle_corner(15)
            pictures.append(pic)
        return max(width_list), total_height, pictures

    @property
    def is_only_one_picture(self) -> bool:
        return not self.text.width and len(self.images) == 1

    @property
    def height(self) -> int:
        width = self.text.width
        if width > 600:
            self.text.wrap(600)
        _, img_height, _ = self._handel_pictures() if self.images else (None, 0, None)
        return self.text.height + img_height + 120
    

    def draw_on_picture(self):
        BackGround = self.background
        Y = self.current_height # 起始位置高度
        X = 155 # 消息框左边缘
        # 头像
        head_img = BuildImage.open(self.head)
        circle_head = head_img.circle().resize((85, 85))
        BackGround.paste(circle_head, (50, Y), circle_head)
        # 昵称
        x_nick = X
        if self.is_robot:
            if config.fakepic_add_bot_icon:
                icon = BuildImage.open(BOT).resize((30, 30))
                BackGround.paste(icon, (x_nick, Y), alpha=True)
                x_nick += 40
        else:
            if config.fakepic_add_level_icon:
                icon = BuildImage.open(LEVEL).resize((70, 25))
                BackGround.paste(icon, (x_nick, Y + 3), alpha=True)
                x_nick += 80
        BackGround.draw_text((x_nick, Y), self.nick_name, fontsize=20, fill=(149, 149, 149), fontname=FONT)
        # 气泡
        if self.is_only_one_picture: #消息内容只有一张图片时不画气泡框
            pass
        else:
            max_width, _, _ = self._handel_pictures() if self.images else (0, None, None)
            if max_width >= self.text.width:
                box_width = max_width + 200
            else:
                box_width = self.text.width + 200
            p_box = (X, Y + 50, box_width, Y + self.height - 30)
            BackGround.draw_rounded_rectangle(
                xy=p_box,
                radius=15,
                fill=(255, 255, 255)
            )
        # 文字
        p_text = (X + 20, Y + 70)
        self.text.draw_on_image(BackGround.image, p_text)
        # 图片
        if self.images:
            _, _, pictures = self._handel_pictures()
            if self.is_only_one_picture:
                BackGround.paste(pictures[0], (X, Y + 50), True)
            else:
                current_pic_height = Y + self.text.height + int(bool(self.text.height)) * 15 + 65
                for pic in pictures:
                    BackGround.paste(pic, (X + 20, current_pic_height), True)
                    current_pic_height += pic.height + 10


def draw_pic(sep_list: list[SeparateMsg], height=1920) -> BytesIO:
    image = BuildImage.new('RGB', (900, height), '#F1F1F1')
    position = 30
    for s in sep_list:
        s.background = image
        s.current_height = position
        position += s.height + 20
        s.draw_on_picture()
    if position > height:
        return draw_pic(sep_list, position)
    result = image.crop((0, 0, 900, position))
    image_bytes = result.save(format='PNG')
    return image_bytes



async def get_user_name(bot: Bot, user_id: int) -> str:
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


async def trans_to_list(bot: Bot, msg: Message) -> list:
    """
    将Message对象拆分成列表
    [{"user_id": int, "is_robot": bool, "messages": ["text": str, "images": [BytesIO]]}, ...]
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
            text = m['text']
            m['images'] = re.findall(r'\[CQ:image,file=.*?url=(.*?)\]', text)
            text = re.sub(r'\[CQ:image,file=.*?url=(.*?)\]', '', text)
            at_id_list = re.findall(r'\[CQ:at,qq=(\d+)\]', text)
            for at_id in at_id_list:
                at_nick = await get_user_name(bot, int(at_id))
                text = re.sub(r'\[CQ:at,qq=(\d+)\]', f'@{at_nick} ', text, 1)
            m['text'] = html.unescape(text)
            for index, url in enumerate(m['images']):
                async with AsyncClient() as cli:
                    res = await cli.get(html.unescape(url))
                    m['images'][index] = BytesIO(res.content)
        is_robot = True if 3889000000 < user_id < 3890000000  else False
        msg_list.append({"user_id": user_id, "is_robot": is_robot, "messages": messages})

    return msg_list



matcher = on_regex(r'^\d{5,10}说', priority=10, block=True)

@matcher.handle()
async def handle(bot: Bot, event: MessageEvent):
    msg_list = await trans_to_list(bot, event.get_message())
    sep_list = []   # 对每一条消息创建一个对象进行绘制
    user_info = {}  # 存放已获取到的用户信息，减少api请求频率
    for user in msg_list:
        user_id = str(user['user_id'])
        if user_id not in user_info:
            async with AsyncClient() as client:
                head = await client.get(f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100")
                img_bytes = BytesIO(head.content)
                nick_name = await get_user_name(bot, int(user_id))
                user_info[user_id] = {"head": img_bytes, "nick_name": nick_name}
        else:
            img_bytes = user_info[user_id]['head']
            nick_name = user_info[user_id]['nick_name']

        for m in user['messages']:
            sep_list.append(SeparateMsg(img_bytes, nick_name, user['is_robot'], m['text'], m['images']))
    
    pic = await asyncio.to_thread(draw_pic, sep_list)
    await matcher.send(MessageSegment.image(pic))
