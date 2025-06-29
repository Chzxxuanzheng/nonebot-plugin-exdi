from nonebot.dependencies import Param

from typing import Any, Self
from typing_extensions import override
import inspect

class ManualParam(Param):
	"""手动参数

	本注入解析所有未匹配到的参数。

	应当放在最后使用。
	"""
	defalut: Any = None

	def __repr__(self) -> str:
		return "ManualParam()"

	@classmethod
	@override
	def _check_param(
		cls, param: inspect.Parameter, allow_types: tuple[type[Param], ...]
	) -> Self:
		return cls(default=param.default)

	@override
	async def _solve(  # pyright: ignore[reportIncompatibleMethodOverride]
		self, **kwargs: Any
	) -> Any:
		if not self.defalut is None:
			return self.defalut
		raise RuntimeError('the param doesn\'t have a defalut value, and don\'t be send a value')