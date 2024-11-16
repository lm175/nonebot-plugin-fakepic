from io import BytesIO

from pathlib import Path
res_path = Path(__file__).parent / "resourse"
BOT = res_path / "bot_icon.png"
LEVEL = res_path / "level_icon.png"

from pil_utils import Text2Image, BuildImage
from .config import config
NICK_FONT = config.fakepic_nick_font
CHAT_FONT = config.fakepic_chat_font
NICK_FALLBACK = config.fakepic_fallback_nickfonts
CHAT_FALLBACK = config.fakepic_fallback_chatfont
NICK_COR = config.fakepic_correct_nick
TEXT_COR = config.fakepic_correct_chat

BOT_ICON = config.fakepic_add_bot_icon
LEVEL_ICON = config.fakepic_add_level_icon


chatfont_size = 32      # 聊天字体大小
chatfont_spacing = 8    # 行间距
nickfont_size = 22      # 昵称字体大小


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
        self.text = Text2Image.from_text(text, chatfont_size, spacing=chatfont_spacing, fontname=CHAT_FONT, fallback_fonts=CHAT_FALLBACK)
        self.images = images

    background: BuildImage
    current_height: int


    @property
    def is_only_one_picture(self) -> bool:
        return not self.text.width and len(self.images) == 1

    @property
    def height(self) -> int:
        width = self.text.width
        if width > 600:
            self.text.wrap(600)
        _, img_height, _ = self._handel_pictures() if self.images else (None, 0, None)
        return img_height + 80 + self.text.height + int(bool(self.text.height)) * 30
    

    def _handel_pictures(self) -> tuple[int, int, list[BuildImage]]:
        if self.is_only_one_picture:
            max_size = 500
            pic_spacing = 0
        else:
            max_size = 300
            pic_spacing = 10
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
            total_height += height + pic_spacing
            pic = pic.resize((width, height)).circle_corner(15)
            pictures.append(pic)
        return max(width_list), total_height, pictures
    

    def draw_on_picture(self):
        BackGround = self.background
        Y = self.current_height # 起始位置高度
        X = 155 # 消息框左边缘
        # 头像
        head_img = BuildImage.open(self.head)
        circle_head = head_img.circle().resize((85, 85))
        BackGround.paste(circle_head, (50, Y), True)
        # 昵称
        x_nick = X
        if self.is_robot:
            if BOT_ICON: # 官方机器人图标
                icon_width = 35
                icon = BuildImage.open(BOT).resize((icon_width, icon_width))
                BackGround.paste(icon, (x_nick, Y), alpha=True)
                x_nick += icon_width + 10
        else:
            if LEVEL: # 用户等级图标
                icon_width = 70
                icon = BuildImage.open(LEVEL).resize((icon_width, int(icon_width * 0.36)))
                BackGround.paste(icon, (x_nick, Y + 3), alpha=True)
                x_nick += icon_width + 10
        p_nick = (x_nick + NICK_COR[0], Y + NICK_COR[1])
        BackGround.draw_text(p_nick, self.nick_name, fontsize=nickfont_size, fill=(149, 149, 149), fontname=NICK_FONT, fallback_fonts=NICK_FALLBACK)
        # 气泡
        if self.is_only_one_picture: #消息内容只有一张图片时不画气泡框
            pass
        else:
            max_width, _, _ = self._handel_pictures() if self.images else (0, None, None)
            if max_width >= self.text.width:
                box_width = max_width + 200
            else:
                box_width = self.text.width + 200
            p_box = (X, Y + 50, box_width, Y + self.height - 20) # 气泡框位置
            BackGround.draw_rounded_rectangle(
                xy=p_box,
                radius=15,
                fill=(255, 255, 255)
            )
        # 文字
        p_text = (X + 22 + TEXT_COR[0], Y + 70 + TEXT_COR[1])
        self.text.draw_on_image(BackGround.image, p_text)
        # 图片
        if self.images:
            _, _, pictures = self._handel_pictures()
            if self.is_only_one_picture:
                BackGround.paste(pictures[0], (X, Y + 50), True)
            else:
                current_pic_height = Y + self.text.height + int(bool(self.text.height)) * 15 + 65
                for pic in pictures:
                    BackGround.paste(pic, (X + 20, current_pic_height), True) # 图片位置
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