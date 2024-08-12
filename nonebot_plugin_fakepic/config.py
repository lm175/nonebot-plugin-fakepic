from pydantic import Extra, BaseModel
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):

    """分隔不同用户的符号"""
    fakepic_user_split: str = "+"

    """分隔相同用户的几条消息"""
    fakepic_message_split: str = " "

    """是否为用户添加等级图标, 默认为True"""
    fakepic_add_level_icon = True

    """是否为官方机器人添加bot图标， 默认为True"""
    fakepic_add_bot_icon = True


config = Config.parse_obj(get_driver().config.dict())