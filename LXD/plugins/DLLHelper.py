import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json
import base64

bot = nonebot.get_bot()


@bot.server_app.route('/getdll', methods=['POST'])
async def getdll():
    data = await request.form
    with open('aaa.bbb', 'rb') as dllfile:
        with open('ccc.ddd', 'rb') as xprfile:
            ret = {
                'payload': {
                    'dll': base64.b64encode(dllfile.read()).decode(),
                    'xpr': base64.b64encode(xprfile.read()).decode()
                },
                'sessionkey': 'ABCD456'}
    return json.dumps(ret)


@bot.server_app.route('/getdlllist', methods=['POST'])
async def getdlllist():
    data = await request.form
    return json.dumps({'payload': [{'id': 1, 'name': '外挂1'}, {'id': 2, 'name': '外挂2'}], 'sessionkey': 'ABCD567'})
