import nonebot
from nonebot import on_command, CommandSession


@on_command('getPlugins', aliases=('插件状态', ), only_to_me=False)
async def getPlugins(session:CommandSession):
    plugins = nonebot.plugin.get_loaded_plugins()
    print(plugins)
    await session.send('我现在支持以下功能：\n\n' +
                       '\n'.join(map(lambda p: p.module, filter(lambda p: p.module, plugins))))
