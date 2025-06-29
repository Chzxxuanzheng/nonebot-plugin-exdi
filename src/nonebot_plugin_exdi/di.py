from nonebot.dependencies import Param
from nonebot.params import (
	DependParam, BotParam, EventParam, StateParam,
	ArgParam, MatcherParam, DefaultParam
)

from typing import Callable, Any, TypeVar, Iterable, Type, TypeAlias
from .dependent import ExDependent
from .params import ManualParam

T = TypeVar('T')
T_Wrapper: TypeAlias = Callable[..., T]
T_Decorator: TypeAlias = Callable[[T_Wrapper[T]], T_Wrapper[T]]

ALLOW_PARAMS_TYPES: tuple[Type[Param], ...] = (  # noqa: UP006
	DependParam,
	BotParam,
	EventParam,
	StateParam,
	ArgParam,
	MatcherParam,
	DefaultParam,
	ManualParam,
)

def di(parameterless: Iterable = []) -> T_Decorator[Any]:
	''' 对函数进行依赖注入,使用过该装饰器后,会在调用时对目标函数自动进行依赖注入 '''
	def decorator(func: T_Wrapper[Any]) -> T_Wrapper[Any]:
		re = ExDependent[Any].parse(
			call=func,
			parameterless=parameterless,
			allow_types=ALLOW_PARAMS_TYPES
		)
		return re
	return decorator