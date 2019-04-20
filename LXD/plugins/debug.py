import nonebot
from quart import request
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import ActionFailed

__plugin_name__ = 'LXD.debug'
bot = nonebot.get_bot()


@on_command('getPlugins', aliases=('插件状态', ), only_to_me=False)
async def getPlugins(session:CommandSession):
    plugins = nonebot.plugin.get_loaded_plugins()
    print(plugins)
    await session.send('已加载的插件列表：\n' +
                       '\n'.join(map(lambda p: p.name, filter(lambda p: p.name, plugins))))


@bot.server_app.route('/bugreport', methods=['POST'])
async def bugnotice():
    data = await request.form
    msg = repr(data)
    try:
        await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
    except ActionFailed as e:
        print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
    return 'success'
