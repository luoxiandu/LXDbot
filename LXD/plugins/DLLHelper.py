import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json

bot = nonebot.get_bot()


@bot.server_app.route('/getdll', methods=['POST'])
async def getdll():
    data = await request.form
    return json.dumps({'payload': {'dll': 'ZnVja2l0', 'xpr': 'ZnVja2l0'}, 'sessionkey': 'ABCD456'})


@bot.server_app.route('/getdlllist', methods=['POST'])
async def getdlllist():
    data = await request.form
    return json.dumps({'payload': [{'id': 1, 'name': '外挂1'}, {'id': 2, 'name': '外挂2'}], 'sessionkey': 'ABCD567'})
