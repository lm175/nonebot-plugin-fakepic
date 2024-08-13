from pydantic import Extra, BaseModel
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):

    """分隔不同用户的符号"""
    fakepic_user_split: str = "+"

    """分隔同一用户的几条消息"""
    fakepic_message_split: str = " "

    """是否为用户添加等级图标"""
    fakepic_add_level_icon: bool = True

    """是否为官方机器人添加bot图标"""
    fakepic_add_bot_icon: bool = True

    """是否删除QQ表情的CQ码"""
    fakepic_del_cqface: bool = True

    """
    使用的字体名称
    修改字体可能导致文字位置发生偏移
    """
    fakepic_nick_font: str = "simhei"    # 昵称字体
    fakepic_chat_font: str = "simhei"    # 聊天字体



config = Config.parse_obj(get_driver().config.dict())