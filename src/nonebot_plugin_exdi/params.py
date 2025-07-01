from nonebot.dependencies import Param

from typing import Any, Optional
from typing_extensions import override, Self
import inspect

class ManualParam(Param):
	"""手动注入参数

	本注入解析未被匹配且没有默认值的参数。
	"""
	def __repr__(self) -> str:
		return "ManualParam()"

	@classmethod
	@override
	def _check_param(
		cls, param: inspect.Parameter, allow_types: tuple[type[Param], ...]
	) -> Optional[Self]:
		if param.default == param.empty:
			return cls()

	@override
	async def _solve(  # pyright: ignore[reportIncompatibleMethodOverride]
		self, **kwargs: Any
	) -> Any:
		raise RuntimeError('manual param should be manually provided')