import nonebot
from quart import request, websocket
from nonebot import on_command, CommandSession
from nonebot.command import call_command
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from aiocqhttp.exceptions import ActionFailed
from LXD.services.DBSvr import DB, SessionkeyManager
import json
import datetime

__plugin_name__ = 'LXD.account'
db = DB()
ssmgr = SessionkeyManager()
bot = nonebot.get_bot()


@on_command('checkBalance', aliases=('查询余额', '查询账户余额', '余额查询', '余额'))
async def checkBalance(session:CommandSession):
    account = session.ctx['user_id']
    balance = db.getbalance(account)
    session.finish("账号" + repr(account) + "的余额为：" + (repr(float(balance) / 100) + '元') if balance is not None else "尚未开户，请充值，充值后自动开户。")


@on_command('setPassword', aliases=('设置密码', '密码设置', '密码'))
async def setPassword(session:CommandSession):
    account = session.ctx['user_id']
    if session.is_first_run:
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
            if session.state['grpid'] not in ['105976356', '869494996']:
                session.finish('您没有权限使用洛仙都客户端，请加入主群：105976356')
        session.state['paid'] = db.cost(account, int(db.getprice('fee')))
    if not session.state['paid']:
        want_to_recharge = session.get('want_to_recharge', prompt='您的余额不足，您想马上充值吗？\n请回复“微信”或“支付宝”，或其它内容取消充值')
        if want_to_recharge in ('支付宝', '微信'):
            await session.send('请充值之后重新发送设置密码指令')
            await call_command(session.bot, session.ctx, name='generalDeposit',
                               current_arg=want_to_recharge + ' ' + str(float(db.getprice('fee')) / 100))
        else:
            session.finish('已取消充值')
    else:
        ensure = session.get('ensure', prompt='您确定要设置密码吗？')
        if ensure in ['确定', '确认', '是', '嗯', '对', '好', '恩恩', '嗯嗯', '好的', '可以', 'OK', '设置']:
            password = session.get('password', prompt='请输入密码：')
            confirm = session.get('confirm', prompt='请确认密码：')
            if password != confirm:
                session.finish('两次输入的密码不一致，已取消设置密码。如需设置请重新发送“设置密码”')
            else:
                db.setpassword(account, password)
                session.finish('密码设置成功！')
        else:
            session.finish('已取消设置密码')


@on_command('setFee', aliases=('设置群费',), only_to_me=False, permission=SUPERUSER)
async def setfee(session:CommandSession):
    price = eval(session.current_arg_text.strip())
    db.setprice('fee', int(price * 100))
    session.finish('设置成功完成')


@on_command('chkonline', aliases=('查询在线',), only_to_me=False, permission=SUPERUSER)
async def chkonline(session:CommandSession):
    msg = '在线者：\n' + '\n'.join(ssmgr.getonlinedetail())
    msg += '\n当前总在线人数：' + str(ssmgr.getonline())
    session.finish(msg)


@on_command('atonline', aliases=('艾特在线', '@在线'), only_to_me=False, permission=SUPERUSER)
async def atonline(session:CommandSession):
    msg = ""
    for online in ssmgr.getVIPonline():
        msg += "[CQ:at,qq=%s] " % online
    session.finish(msg)


@on_command('compensateonline', aliases=('补偿在线', '奖励在线'), only_to_me=False, permission=SUPERUSER, shell_like=True)
async def compensateonline(session:CommandSession):
    msg = "已成功为 "
    for online in ssmgr.getVIPonline():
        await call_command(session.bot, session.ctx, name='generalManualDeposit', current_arg=online + ' ' + session.argv[0], disable_interaction=True)
        msg += online + ' '
    msg += "补偿/奖励 " + session.argv[0] + " 元！"
    session.finish(msg)


@on_command('kick', aliases=('踢',), only_to_me=False, permission=SUPERUSER, shell_like=True)
async def kickhandler(session:CommandSession):
    account = session.argv[0]
    if ssmgr.clearSessionkey(account):
        msg = '踢 ' + account + ' 成功！'
        logger.info('用户' + str(session.ctx['user_id']) + '踢了用户' + account)
    else:
        msg = '踢除过程中出错，可能已经离线！'
    session.finish(msg)


@on_command('ban', aliases=('封禁', ), only_to_me=False, permission=SUPERUSER, shell_like=True)
async def ban(session:CommandSession):
    account = session.argv[0]
    db.ban(account)
    session.finish('已提交封禁请求')


@on_command('unban', aliases=('解封', ), only_to_me=False, permission=SUPERUSER, shell_like=True)
async def unban(session:CommandSession):
    account = session.argv[0]
    db.unban(account)
    session.finish('已提交解封请求')


@on_command('getversion', aliases=('查询版本',), only_to_me=False, permission=SUPERUSER)
async def getversion(session:CommandSession):
    session.finish('当前版本为：' + db.getvar('current_version'))


@on_command('setversion', aliases=('设置版本',), only_to_me=False, permission=SUPERUSER, shell_like=True)
async def setversion(session:CommandSession):
    db.setvar('current_version', session.argv[0])
    session.finish('设置成功！当前版本为：' + db.getvar('current_version'))


@bot.server_app.route('/login', methods=['POST'])
async def loginhandler():
    data = await request.form
    acc = data['username']
    pwd = data['password']
    ret = {}
    if db.isbanned(acc):
        ret['status'] = 'banned'
        logger.info('login ret: ' + str(ret))
        return json.dumps(ret)
    if acc and pwd and db.chkpassword(acc, pwd) and data['version'] == db.getvar('current_version'):
        db.varpp('logincount')
        db.varpp('logincountday')
        db.statistics_loginpp(acc)
        ret['status'] = 'success'
        ret['sessionkey'] = ssmgr.newSessionkey(acc)
        logger.info('用户' + acc + '已登录上线 IP：' + request.remote_addr)
    else:
        ret['status'] = 'failed'
    logger.info('login ret: ' + str(ret))
    return json.dumps(ret)


@bot.server_app.route('/passkeylogin', methods=['POST'])
async def passkeyloginhandler():
    data = await request.form
    passkey = data['passkey']
    HWID = data['HWID']
    ret = {}
    if passkey and HWID and db.checkPassKey(passkey, HWID) and db.validHWID(HWID):
        db.varpp('logincount')
        db.varpp('logincountday')
        db.statistics_loginpp(HWID)
        ret['status'] = 'success'
        ret['payload'] = {
            'remaining': db.checkPassKeyRemainingTime(passkey)
        }
        logger.info('用户' + passkey + '已登录上线 IP：' + request.remote_addr)
    else:
        ret['status'] = 'failed'
    logger.info('login ret: ' + str(ret))
    return json.dumps(ret)


@bot.server_app.route('/requesttrial', methods=['POST'])
async def triallogin():
    data = await request.form
    IP = request.remote_addr
    HWID = data['HWID']
    ret = {}
    if db.isbanned(HWID):
        ret['status'] = 'banned'
        return json.dumps(ret)
    if ssmgr.isonline(HWID) and data['version'] == db.getvar('current_version'):
        ret['status'] = 'success'
        ret['sessionkey'] = ssmgr.newSessionkey(HWID)
        logger.info('用户' + HWID + '在试用时间限制内已重新上线')
    elif HWID and IP and data['version'] == db.getvar('current_version') and (db.chktrialonce(HWID) or True) and db.validHWID(HWID):
        db.newtrial(HWID, IP)
        db.varpp('logincount')
        db.varpp('logincountday')
        db.statistics_loginpp(HWID)
        ret['status'] = 'success'
        ret['sessionkey'] = ssmgr.newSessionkey(HWID)
        nonebot.scheduler.add_job(kickbeggar, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=60), args=[HWID], id=HWID, replace_existing=True)
        logger.info('用户' + HWID + '已获取新的试用时间并登录')
    else:
        ret['status'] = 'failed'
    logger.info('requesttrial ret: ' + str(ret))
    return json.dumps(ret)


async def kickbeggar(HWID):
    ssmgr.clearSessionkey(HWID)
    logger.info('试用用户' + HWID + '登录到期')


@bot.server_app.route('/getaccountinfo', methods=['POST'])
async def replyaccountinfo():
    data = await request.form
    sessionkey = data['sessionkey']
    account = sessionkey.split("::")[0]
    if account.isdigit():
        grplst = await bot.get_group_list()
        for grp in grplst:
            try:
                info = await bot.get_group_member_info(group_id=grp['group_id'], user_id=account)
            except ActionFailed:
                continue
            if info.get('group_id') == grp['group_id']:
                grpid = str(info['group_id'])
    ret = {}
    if sessionkey and ssmgr.checkSessionkey(sessionkey) and data['version'] == db.getvar('current_version'):
        ret['status'] = 'success'
        if account.isdigit():
            ret['payload'] = {
                'balance': float(db.getbalance(account)) / 100 if account.isdigit() else 0.0,
                'isBeggar': False,
                'prices': {
                    'megalodon': float(db.getprice('megalodon_' + grpid) / 100.0),
                    'whale': float(db.getprice('whale_' + grpid) / 100.0),
                    'greatwhite': float(db.getprice('greatwhite_' + grpid) / 100.0),
                    'bullshark': float(db.getprice('bullshark_' + grpid) / 100.0),
                    'tigershark': float(db.getprice('tigershark_' + grpid) / 100.0),
                    'redshark': float(db.getprice('redshark_' + grpid) / 100.0),
                    'level': float(db.getprice('level_' + grpid) / 100.0),
                    'unlock': float(db.getprice('unlock_' + grpid) / 100.0),
                }
            }
        else:
            ret['payload'] = {
                'balance': float(db.getbalance(account)) / 100 if account.isdigit() else 0.0,
                'isBeggar': True,
            }
        ret['sessionkey'] = sessionkey # db.newSessionkey(sessionkey.split("::")[0])
    else:
        ret['status'] = 'failed'
    logger.info('getaccountinfo ret: ' + str(ret))
    return json.dumps(ret)


@bot.server_app.websocket('/chklogin/<uid>')
async def chklogin(uid):
    lastmsg = '无'
    blockthis = True
    try:
        while True:
            try:
                sessionkey = await websocket.receive()
                if (sessionkey.split("::")[0] == uid and ssmgr.checkSessionkey(sessionkey)) or (ssmgr.getSessionkey(uid) and sessionkey == lastmsg):
                    msg = ssmgr.newSessionkey(sessionkey.split("::")[0])
                    await websocket.send(msg)
                    lastmsg = msg
                elif sessionkey == 'bye':
                    blockthis = False
                    await websocket.send('bye')
                else:
                    msg = '*failed*'
                    await websocket.send(msg)
                    blockthis = False
                    acc = sessionkey.split('::')[0]
                    logger.info('用户' + acc + '认证失败\n接收的sessionkey: ' + sessionkey + '\n正确的sessionkey: ' + str(ssmgr.getSessionkey(acc)) + '\n上次的返回: ' + lastmsg)
            except (TypeError, IndexError, ValueError, KeyError):
                msg = '*failed*'
                await websocket.send(msg)
    finally:
        if blockthis:
            db.ban(uid)
            logger.info(str(uid) + '出现数据异常-退出时未道别 IP：' + request.remote_addr)
            await bot.send_group_msg_rate_limited(group_id=869494996, message=str(uid) + '出现数据异常-退出时未道别')
        ssmgr.clearSessionkey(uid)
        logger.info('用户' + uid + '断开连接')


