from pydantic import BaseModel, field_validator
from nonebot import get_plugin_config


class Config(BaseModel):

    fakepic_user_split: str = "+"
    """分隔不同用户的符号"""

    fakepic_message_split: str = " "
    """分隔同一用户的几条消息"""

    fakepic_nick_start: str = "【"
    """获取昵称位置的起始符号"""
    
    fakepic_nick_end:   str = "】"
    """获取昵称位置的终止符号"""

    fakepic_add_level_icon: bool = True
    """是否为用户添加等级图标"""

    fakepic_add_bot_icon: bool = True
    """是否为官方机器人添加bot图标"""

    fakepic_del_cqface: bool = True
    """是否删除QQ表情的CQ码"""

    fakepic_nick_font: str = ""
    """昵称首选字体"""

    fakepic_chat_font: str = ""
    """聊天首选字体"""

    fakepic_fallback_nickfonts: list[str] = []
    """昵称备选字体"""
    
    fakepic_fallback_chatfont: list[str] = []
    """聊天备选字体"""

    fakepic_correct_nick: list[int] = [0, 0]    # 昵称字体
    fakepic_correct_chat: list[int] = [0, 0]    # 聊天字体
    """如果文字位置发生偏移，可视情况修改此项进行修正"""

    @field_validator("fakepic_nick_start", "fakepic_nick_end")
    @classmethod
    def check_str(cls, s: str) -> str:
        ban = ['[', ']', '&']   # 被转义的符号
        if s not in ban:
            return s
        raise ValueError(f"“{s}” 请勿使用该字符获取昵称！")



config = get_plugin_config(Config)