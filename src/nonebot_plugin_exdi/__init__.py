from nonebot.plugin import PluginMetadata

from .config import Config, config

__plugin_meta__ = PluginMetadata(
	name="依赖注入扩展",
	description="允许对非handle函数进行依赖注入",
	usage=(
		'声明依赖: `require("nonebot_plugin_exdi")\n'
		'导入初始化函数，依赖注入装饰器: `from nonebot_plugin_exdi import init_di, di`\n'
		'初始化: `matcher,handle(parameterless=[init_di()])`\n'
		'装饰函数: `@di()`\n'
	),
	config=Config,
	homepage="https://github.com/Chzxxuanzheng/nonebot-plugin-exdi",
    type="library",
    supported_adapters=None,
)

from .di import di as di
from .baseparams import init_di as init_di, DiBaseParamsManager as DiBaseParamsManager
from .overwrite import overwrite_handle_event as overwrite_handle_event, overwrite_check as overwrite_check

if config.exdi_overwrite_nb:
	overwrite_check()
	overwrite_handle_event()