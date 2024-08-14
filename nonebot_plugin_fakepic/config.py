from pydantic import BaseModel
from nonebot import get_plugin_config


class Config(BaseModel):

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

    """使用的字体名称"""
    fakepic_nick_font: str = ""    # 昵称字体
    fakepic_chat_font: str = ""    # 聊天字体

    """如果文字位置发生偏移，可视情况修改以下配置进行修正"""
    fakepic_correct_nick: list = [0, 0]    # 昵称
    fakepic_correct_chat: list = [0, 0]    # 聊天文字



config = get_plugin_config(Config)