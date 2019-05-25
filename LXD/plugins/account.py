import nonebot
from quart import request, websocket
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from aiocqhttp.exceptions import ActionFailed
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from LXD.services.DBSvr import DB
import json
import datetime

__plugin_name__ = 'LXD.account'
db = DB()
bot = nonebot.get_bot()
sched = AsyncIOScheduler()
sched.start()


@on_command('checkBalance', aliases=('查询余额', '查询账户余额', '余额查询', '余额'))
async def checkBalance(session:CommandSession):
    account = session.ctx['user_id']
    balance = db.getbalance(account)
    session.finish("账号" + repr(account) + "的余额为：" + (repr(float(balance) / 100) + '元') if balance is not None else "尚未开户，请充值，充值后自动开户。")


@on_command('setPassword', aliases=('设置密码', ))
async def setPassword(session:CommandSession):
    account = session.ctx['user_id']
    if not session.state.get('grpid'):
        try:
            session.state['grpid'] = str(session.ctx['group_id'])
        except KeyError:
            grplst = await bot.get_group_list()
            for grp in grplst:
                try:
                    info = await bot.get_group_member_info(group_id=grp['group_id'], user_id=account)
                except ActionFailed:
                    continue
                if info.get('group_id') == grp['group_id']:
                    session.state['grpid'] = str(info['group_id'])
        if session.state['grpid'] not in ['105976356']:
            session.finish('您没有权限使用洛仙都客户端，请加入主群：105976356')
    ensure = session.get('ensure', prompt='您确定要设置密码吗？')
    if ensure in ['确定', '确认', '是', '设置']:
        password = session.get('password', prompt='请输入密码：')
        confirm = session.get('confirm', prompt='请确认密码：')
        if password != confirm:
            session.finish('两次输入的密码不一致，已取消设置密码。如需设置请重新发送“设置密码”')
        else:
            db.setpassword(account, password)
            session.finish('密码设置成功！')
    else:
        session.finish('已取消设置密码')


@bot.server_app.route('/login', methods=['POST'])
async def loginhandler():
    data = await request.form
    acc = data['username']
    pwd = data['password']
    ret = {}
    if acc and pwd and db.chkpassword(acc, pwd):
        db.varpp('logincount')
        db.varpp('logincountday')
        ret['status'] = 'success'
        ret['sessionkey'] = db.newSessionkey(acc)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.route('/requesttrial', methods=['POST'])
async def triallogin():
    data = await request.form
    IP = request.remote_addr
    HWID = data['HWID']
    ret = {}
    if HWID and IP and db.chktrial(HWID):
        db.newtrial(HWID, IP)
        db.varpp('logincount')
        db.varpp('logincountday')
        ret['status'] = 'success'
        ret['sessionkey'] = db.newSessionkey(HWID)
        sched.add_job(kickbeggar, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=60), args=[HWID], id=HWID, replace_existing=True)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


async def kickbeggar(HWID):
    db.clearSessionkey(HWID)


@bot.server_app.route('/getaccountinfo', methods=['POST'])
async def replyaccountinfo():
    data = await request.form
    sessionkey = data['sessionkey']
    ret = {}
    if sessionkey and db.checkSessionkey(sessionkey):
        account = sessionkey.split("::")[0]
        ret['status'] = 'success'
        ret['payload'] = {
            'balance': float(db.getbalance(account)) / 100 if account.isdigit() else 0.0,
            'isBeggar': not account.isdigit()
        }
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)


@bot.server_app.websocket('/chklogin')
async def chklogin():
    while True:
        sessionkey = await websocket.receive()
        await websocket.send(db.newSessionkey(sessionkey.split("::")[0]) if sessionkey and db.checkSessionkey(sessionkey) else '*failed*')
