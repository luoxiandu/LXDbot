import nonebot
from nonebot import on_command, CommandSession

__plugin_name__ = '错误排查器'


@on_command('getPlugins', aliases=('插件状态', ), only_to_me=False)
async def getPlugins(session:CommandSession):
    plugins = nonebot.plugin.get_loaded_plugins()
    print(plugins)
    await session.send('已加载的插件列表：\n' +
                       '\n'.join(map(lambda p: p.name, filter(lambda p: p.name, plugins))))
