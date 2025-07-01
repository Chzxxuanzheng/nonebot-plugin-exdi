from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State, T_DependencyCache
from nonebot.params import Depends

from contextvars import ContextVar
from contextlib import AsyncExitStack
from typing import Any, Optional

from .config import config

current_di_base_params: ContextVar[Optional[dict[str, Any]]] = ContextVar('current_di_base_params', default=None)

async def _init_di(bot: Bot, event: Event, state: T_State) -> None:
	if config.isOverwrite():
		logger.opt(colors=True).warning('You have overwrite the <b>handle_event</b> function, <b>init_di</b> is not necessary')
		return
	caches: T_DependencyCache = {}
	current_di_base_params.set({
		'bot': bot,
		'event': event,
		'state': state,
		'stack': None,
		'dependency_cache': caches,
	})

def init_di() -> Any:
	return Depends(_init_di)

class DiBaseParamsManager:
	""" 依赖注入的基本参数类
	用于重写handle_event时获取stack和dependence_caches
	不需要重写handle_event时请勿动 """
	bot: Bot
	event: Event
	state: T_State
	stack: AsyncExitStack
	dependency_cache: T_DependencyCache

	def __init__(self, bot: Bot, event: Event):
		self.bot = bot
		self.event = event

	async def __aenter__(self) -> 'DiBaseParamsManager':
		self.state = {}
		self.dependency_cache = {}
		self.stack = await AsyncExitStack().__aenter__()
		current_di_base_params.set({
			'bot': self.bot,
			'event': self.event,
			'state': self.state,
			'stack': self.stack,
			'dependency_cache': self.dependency_cache,
		})
		return self

	async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		await self.stack.__aexit__(exc_type, exc_val, exc_tb)

	def getParam(self) -> dict[str, Any]:
		""" 获取当前的参数 """
		return current_di_base_params.get() or {}