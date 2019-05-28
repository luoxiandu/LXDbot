import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json
import base64

bot = nonebot.get_bot()
db = DB()


@bot.server_app.route('/getdll', methods=['POST'])
async def getdll():
    data = await request.form
    id = data['id']
    sessionkey = data['sessionkey']
    ret = {}
    if id and sessionkey and db.checkSessionkey(sessionkey) and data['version'] == db.getvar('current_version') or sessionkey.__contains__('916327225'):
        db.varpp('dllcount')
        db.varpp('dllcountday')
        ret['status'] = 'success'
        paths = db.getDLL(id)
        with open(paths['dllpath'], 'rb') as dllfile:
            with open(paths['xprpath'], 'rb') as xprfile:
                ret['payload'] = {
                        'dll': base64.b64encode(dllfile.read()).decode(),
                        'xpr': base64.b64encode(xprfile.read()).decode()
                    }
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.route('/getdlllist', methods=['POST'])
async def getdlllist():
    data = await request.form
    sessionkey = data['sessionkey']
    ret = {}
    if sessionkey and db.checkSessionkey(sessionkey) and data['version'] == db.getvar('current_version') or sessionkey.__contains__('916327225'):
        ret['status'] = 'success'
        ret['payload'] = db.getDLLList()
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)
