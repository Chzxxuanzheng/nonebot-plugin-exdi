from nonebot.dependencies import Dependent
from nonebot.internal.matcher import current_matcher
from typing import Any, Callable, TypeVar, cast
from typing_extensions import override
from nonebot.utils import run_coro_with_shield
from nonebot.compat import ModelField
from exceptiongroup import ExceptionGroup
import anyio

from .baseparams import current_di_base_params

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
		
		re, err = anyio.from_thread.run(self.solve, **params) # type: ignore
		
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


