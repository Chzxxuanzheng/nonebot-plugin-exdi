<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-exdi

_✨ 依赖注入扩展,将依赖注入的范围从钩子扩展到其他函数 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/chzxxuanzheng/nonebot-plugin-exdi.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-template">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-exdi.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="python">

</div>

## 📖 介绍

该插件允许在Matcher响应范围内,对所有调用的函数使用依赖注入向上下文获取参数,不再需要handle函数传参了

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-exdi

</details>

<details open>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-exdi
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-exdi
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-exdi
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-exdi
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_exdi"]

</details>

## ⚙️ 使用说明

<details open>
<summary>一般使用</summary>

```python
exdi = require("nonebot_plugin_exdi")
matcher1 = on_command('cs')

@matcher1.handle(parameterless=[exdi.init_di()])
async def my_handle():
	await my_func1()

@exdi.di()
async def my_func1(bot: Bot, matcher: Matcher, arg: Message = CommandArg()):
	await matcher.send(f'你的bot是:{bot}')
	await matcher.send(f'收到的参数是:{arg}')
```
运行结果:

![结果](https://github.com/Chzxxuanzheng/nonebot-plugin-exdi/blob/master/resources/img1.png?raw=true)
</details>

<details open>
<summary>自定义Depends支持</summary>

```python
exdi = require("nonebot_plugin_exdi")

def _depend1(bot: Bot, event: Event):
	# do someting
	return 'depend1返回值'

def _depend2(bot: Bot, event: Event):
	# do someting
	return 'depend2返回值'

depend1 = Annotated[str, Depends(_depend1)]
depend2 = Depends(_depend2)

@dataclass
class ClassDependency:
	event: Event
	depend1: depend1

	def __str__(self) -> str:
		return f'(event type:{self.event.get_type()}, depend1: {self.depend1})'

classDepend = Annotated[ClassDependency, Depends(ClassDependency)]

matcher1 = on_command('cs')

@matcher1.handle(parameterless=[exdi.init_di()])
async def my_handle():
	for msg in my_func2():
		await matcher1.send(msg)

@exdi.di()
def my_func2(d1: depend1, classDepend: classDepend, d2: str = depend2):
	yield f'depend1: {d1}, depend2: {d2}'
	yield f'classDepend: {classDepend}'
```
运行结果:

![结果](https://github.com/Chzxxuanzheng/nonebot-plugin-exdi/blob/master/resources/img2.png?raw=true)
</details>

<details open>
<summary>手动传入参数，默认值参数支持</summary>

```python
exdi = require("nonebot_plugin_exdi")

matcher1 = on_command('cs')

@matcher1.handle(parameterless=[exdi.init_di()])
async def my_handle():
	await my_func3(arg1='cillo world')

@exdi.di()
async def my_func3(matcher: Matcher, arg1: str, arg2: str = 'defaultValue'):
	await matcher.send(f'arg1: {arg1}')
	await matcher.send(f'arg2: {arg2}')
```
运行结果:

![结果](https://github.com/Chzxxuanzheng/nonebot-plugin-exdi/blob/master/resources/img3.png?raw=true)
</details>

**注意,通常情况下不支持生成器依赖,同时不和matcher共用缓存。这是由于nonebot不对外暴漏`dependency_cache`和`stack`,缓存需要`dependency_cache`,生成器依赖需要`stack`。如果有需要请参考下面的`重写NoneBot`。**

### 重写NoneBot事件发布函数

搞清楚你在做什么后再继续往下看,如果你**不了解nonebot的运作规律,请勿使用该项**

<details>
如果想要更好的运行效果,必须要重写`nonebot.message.handle_event`函数来获取`dependency_cache`和`stack`。重写该函数后不再需要`init_di`来初始化依赖注入。

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| exdi_overwrite_nb | 否 | False | 重写`nonebot`的`nonebot.message.handle_event`函数 |
| exdi_hand_overwrite | 否 | False | 你手动重写`nonebot.message.handle_event`函数 |

你可以通过设置`exdi_overwrite_nb`为`True`来让插件自己覆盖`handle_event`,但注意的是插件需要在

你也可以自己手动重写`handle_event`,并且符合一下要求:

将原handle_event处创建stack的代码
```python
async with AsyncExitStack() as stack:
```
替换为以下代码
```python
exdi = require("nonebot_plugin_exdi")

async with exdi.DiBaseParamsManager(bot=bot, event=event) as base_params:
```

DiBaseParamsManager的模型设计
| 属性 | 说明 |
|:---:|:----|
|bot|bot|
|event|event|
|state|state|
|stack|stack|
|dependency_cache|dependency_cache|

完成重写后,你可以把`exdi_overwrite_nb`设置为`False`,把`exdi_hand_overwrite`设置为`True`。此时插件不会尝试重写`handle_event`,但同时会按照重写过`handle_event`的逻辑运行
</details>


## 结尾
readme模板来自[A-kirami](https://github.com/A-kirami/nonebot-plugin-template/)

这是萌新的第一个插件,异步学的有限...有问题,大佬不要骂了,欢迎提issue
