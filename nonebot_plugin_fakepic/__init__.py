from nonebot.plugin import PluginMetadata
from .config import Config, config

__plugin_meta__ = PluginMetadata(
    name="聊天截图伪造",
    description="伪造QQ聊天截图",
    usage="qq说...+qq说...",
    type="application",
    homepage="{项目主页}",
    # 发布必填。
    config=Config,
    supported_adapters={"~onebot.v11"},
)

from . import __main__ 