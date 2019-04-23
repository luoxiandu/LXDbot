import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json

bot = nonebot.get_bot()


@bot.server_app.route('/getdll', methods=['POST'])
async def getdll():
    data = await request.formk
    return json.dumps({'payload': 'ZnVja2l0', 'sessionkey': 'ABCD456'})
