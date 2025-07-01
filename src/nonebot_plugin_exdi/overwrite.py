OVERWRITE_VERSION = ['2.4.2']

def overwrite_check() -> None:
	''' 检测是否适合覆盖，一般handle_event被适配器使用，本函数仅检测适配器加载情况 '''
	from sys import modules

	load_adapter_name = []
	for name in list(modules.keys()):
		if name.startswith('nonebot.adapters.'):
			name = name.replace('nonebot.adapters.', '').split('.')[0]
			if name not in load_adapter_name: load_adapter_name.append(name)

	if load_adapter_name:
		raise RuntimeError(
			f'You have already loaded adapters({", ".join(load_adapter_name)}), overwriting handle_event won\'t work, you should load these plugin before loading adapters.'
		)

def overwrite_handle_event() -> None:
	''' 覆盖handle_event函数

	 **请确保你知道NoneBot事件运作机制再使用** '''

	import importlib
	import nonebot
	from nonebot.internal.matcher import matchers
	from nonebot.exception import  NoLogException, StopPropagation
	from nonebot.adapters import Bot, Event
	from nonebot.message import _apply_event_preprocessors, _handle_exception, check_and_run_matcher, _apply_event_postprocessors
	from nonebot.utils import escape_tag, run_coro_with_shield
	from nonebot.rule import TrieRule
	from nonebot import logger

	from exceptiongroup import catch, BaseExceptionGroup
	import anyio

	from .baseparams import DiBaseParamsManager

	if nonebot.__version__ not in OVERWRITE_VERSION:
		logger.warning(
			f'You are using NoneBot version {nonebot.__version__}, but this plugin\'s overwrite is designed for version {", ".join(OVERWRITE_VERSION)}. '
			'This may cause unexpected issues, please check the plugin compatibility.'
			'Please create an issue on https://github.com/Chzxxuanzheng/nonebot-plugin-exdi/issues'
		)

	async def handle_event(bot: Bot, event: Event) -> None:
		show_log = True
		log_msg = f"<m>{escape_tag(bot.type)} {escape_tag(bot.self_id)}</m> | "
		try:
			log_msg += event.get_log_string()
		except NoLogException:
			show_log = False
		if show_log:
			logger.opt(colors=True).success(log_msg)

		async with DiBaseParamsManager(bot=bot, event=event) as base_params:
			if not await _apply_event_preprocessors(
				**base_params.getParam()
			):
				return

			# Trie Match
			try:
				TrieRule.get_value(bot, event, base_params.state)
			except Exception as e:
				logger.opt(colors=True, exception=e).warning(
					"Error while parsing command for event"
				)

			break_flag = False

			def _handle_stop_propagation(exc_group: BaseExceptionGroup) -> None:
				nonlocal break_flag

				break_flag = True
				logger.debug("Stop event propagation")

			# iterate through all priority until stop propagation
			for priority in sorted(matchers.keys()):
				if break_flag:
					break

				if show_log:
					logger.debug(f"Checking for matchers in priority {priority}...")

				if not (priority_matchers := matchers[priority]):
					continue

				with catch(
					{
						StopPropagation: _handle_stop_propagation,
						Exception: _handle_exception(
							"<r><bg #f8bbd0>Error when checking Matcher.</bg #f8bbd0></r>"
						),
					}
				):
					async with anyio.create_task_group() as tg:
						for matcher in priority_matchers:
							tg.start_soon(
								run_coro_with_shield,
								check_and_run_matcher(
									matcher,
									bot,
									event,
									base_params.state.copy(),
									base_params.stack,
									base_params.dependency_cache,
								),
							)

			if show_log:
				logger.debug("Checking for matchers completed")

			await _apply_event_postprocessors(**base_params.getParam())

	importlib.import_module('nonebot.message').handle_event = handle_event # type: ignore
	logger.success('Overwrite handle_event function successfully')