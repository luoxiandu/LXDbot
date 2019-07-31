import nonebot
import config
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from LXD.services.DBSvr import DB, SessionkeyManager
import json
import base64

bot = nonebot.get_bot()
db = DB()
ssmgr = SessionkeyManager()


@bot.server_app.route('/getdll', methods=['POST'])
async def getdll():
    data = await request.form
    id = data['id']
    sessionkey = data['sessionkey']
    ret = {}
    if db.isbanned(sessionkey.split('::')[0]):
        ret['status'] = 'banned'
        return json.dumps(ret)
    if id and sessionkey and ssmgr.checkSessionkey(sessionkey) and data['version'] == db.getvar('current_version'):
        db.varpp('dllcount')
        db.varpp('dllcountday')
        db.statistics_injectpp(sessionkey.split('::')[0])
        ret['status'] = 'success'
        paths = db.getDLL(id)
        with open(paths['dllpath'], 'rb') as dllfile:
            with open(paths['xprpath'], 'rb') as xprfile:
                    ret['payload'] = {
                            'dll': base64.b64encode(dllfile.read()).decode(),
                            'xpr': base64.b64encode(xprfile.read()).decode(),
                        }
        if paths['resourcepath']:
            with open(paths['resourcepath'], 'rb') as rcfile:
                ret['payload']['resource'] = base64.b64encode(rcfile.read()).decode()
        if paths['keypath']:
            with open(paths['keypath'], 'rb') as rcfile:
                ret['payload']['keyfile'] = base64.b64encode(rcfile.read()).decode()
                ret['payload']['keyfilename'] = paths['keypath'].split('/')[-1]
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
        await bot.send_group_msg_rate_limited(group_id=config.notice_group,
                                              message='用户' + sessionkey.split('::')[0] + '已注入DLL IP：' + request.remote_addr)
        logger.info('用户' + sessionkey.split('::')[0] + '已注入DLL IP：' + request.remote_addr)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.route('/getdlllist', methods=['POST'])
async def getdlllist():
    data = await request.form
    sessionkey = data['sessionkey']
    ret = {}
    if db.isbanned(sessionkey.split('::')[0]):
        ret['status'] = 'banned'
        return json.dumps(ret)
    if sessionkey and ssmgr.checkSessionkey(sessionkey) and data['version'] == db.getvar('current_version'):
        ret['status'] = 'success'
        ret['payload'] = db.getDLLList(2) if sessionkey.split('::')[0].isdigit() else db.getDLLList(1)
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.route('/passkeygetdll', methods=['POST'])
async def passkeygetdll():
    data = await request.form
    dllid = data['id']
    passkey = data['passkey']
    HWID = data['HWID']
    ret = {}
    if passkey and HWID and db.checkPassKey(passkey, HWID):
        db.varpp('dllcount')
        db.varpp('dllcountday')
        ret['status'] = 'success'
        paths = db.getDLL(dllid)
        with open(paths['dllpath'], 'rb') as dllfile:
            with open(paths['xprpath'], 'rb') as xprfile:
                    ret['payload'] = {
                            'dll': base64.b64encode(dllfile.read()).decode(),
                            'xpr': base64.b64encode(xprfile.read()).decode(),
                        }
        if paths['resourcepath']:
            with open(paths['resourcepath'], 'rb') as rcfile:
                ret['payload']['resource'] = base64.b64encode(rcfile.read()).decode()
        await bot.send_group_msg_rate_limited(group_id=config.notice_group,
                                              message='用户' + passkey + '已注入DLL IP：' + request.remote_addr)
        logger.info('用户' + passkey + '已注入DLL IP：' + request.remote_addr)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.route('/passkeygetdlllist', methods=['POST'])
async def passkeygetdlllist():
    data = await request.form
    passkey = data['passkey']
    HWID = data['HWID']
    ret = {}
    if passkey and HWID and db.checkPassKey(passkey, HWID):
        ret['status'] = 'success'
        ret['payload'] = db.getDLLList(2)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)

