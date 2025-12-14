from nonebot.dependencies import Dependent
from nonebot.internal.matcher import current_matcher
from nonebot import get_driver
from typing import Any, Callable, TypeVar, cast
from typing_extensions import override
from nonebot.utils import run_coro_with_shield
from nonebot.compat import ModelField
from exceptiongroup import ExceptionGroup
import threading
import anyio
from anyio.from_thread import BlockingPortal, start_blocking_portal
from contextlib import AbstractContextManager

from .baseparams import current_di_base_params

_portal_lock = threading.Lock()
_portal_cm: AbstractContextManager[BlockingPortal] | None = None
_portal: BlockingPortal | None = None

def _get_portal() -> BlockingPortal:
    global _portal, _portal_cm
    with _portal_lock:
        if _portal is None:
            _portal_cm = start_blocking_portal()
            _portal = _portal_cm.__enter__()
    return _portal

@get_driver().on_shutdown
def _close_portal() -> None:
    global _portal_cm, _portal
    if _portal_cm is not None:
        _portal_cm.__exit__(None, None, None)
        _portal_cm = None
        _portal = None

R = TypeVar("R")

class ExDependent(Dependent[R]):
	"""扩展的依赖注入类，继承自 `Dependent`"""
	
	@override
	def __call__(self, **kwargs: Any) -> R: # type: ignore
		self.run_params = []
		
		for param in self.params:
			if param.name in kwargs:continue
			self.run_params.append(param)

		params = current_di_base_params.get()
		if not params:
			raise RuntimeError("please call init_di() or set overwrite_nb to true before using extend dependence injection")
		params = params.copy()
		params.update({'matcher': current_matcher.get()}) # 追加 matcher
		
		async def self_solve():
			return await self.solve(**params)

		re, err = _get_portal().call(self_solve) # type: ignore
		
		if err:
			# If there are any exceptions, raise them as a group
			# This allows us to handle multiple errors at once
			raise ExceptionGroup(
				f'error when dependence inject, {", ".join([f"`{k}`" for k in err.keys()])} parse failed',
				list(err.values())
			)

		kwargs.update(**re)

		return cast(Callable[..., R], self.call)(**kwargs)

	@override
	async def solve(self, **params: Any) -> tuple[dict[str, Any], dict[str, Exception]]: # type: ignore
		await self.check(**params)

		# solve parameterless
		for param in self.parameterless:
			await param._solve(**params)

		# solve param values
		result: dict[str, Any] = {}
		errorDict: dict[str, Exception] = {}
		if not self.run_params:
			return result, {}

		async def _solve_field(field: ModelField, params: dict[str, Any]) -> None:
			try:
				value = await self._solve_field(field, params)
				result[field.name] = value
			except Exception as e:
				# collect exceptions for later handling
				errorDict[field.name] = e

		async with anyio.create_task_group() as tg:
			for field in self.run_params:
				# shield the task to prevent cancellation
				# when one of the tasks raises an exception
				# this will improve the dependency cache reusability
				tg.start_soon(run_coro_with_shield, _solve_field(field, params))

		return result, errorDict


