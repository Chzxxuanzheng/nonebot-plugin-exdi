from pydantic import BaseModel
from nonebot import get_plugin_config

class Config(BaseModel):
	"""Plugin Config Here"""
	exdi_overwrite_nb: bool = False
	''' 覆盖 nonebot 的 handle_event 函数来拿到不对外开放的stack与dependece_caches '''
	exdi_hand_overwrite: bool = False
	''' 你手动覆盖了nonebot 的 handle_event 函数来拿到不对外开放的stack与dependece_caches '''

	def isOverwrite(self) -> bool:
		"""是否覆盖了 nonebot 的 handle_event 函数"""
		return self.exdi_overwrite_nb or self.exdi_hand_overwrite

config: Config = get_plugin_config(Config)