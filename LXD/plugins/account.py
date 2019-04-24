import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json

__plugin_name__ = 'LXD.account'
db = DB()
bot = nonebot.get_bot()


@on_command('checkBalance', aliases=('查询余额', '查询账户余额', '余额查询', '余额'))
async def checkBalance(session:CommandSession):
    account = session.ctx['user_id']
    balance = db.getbalance(account)
    session.finish("账号" + repr(account) + "的余额为：" + (repr(float(balance) / 100) + '元') if balance is not None else "尚未开户，请充值，充值后自动开户。")

@on_command('setPassword', aliases=('设置密码', ))
async def setPassword(session:CommandSession):
    account = session.ctx['user_id']
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
        ret['status'] = 'success'
        ret['sessionkey'] = db.newSessionkey(acc)
    else:
        ret['status'] = 'failed'
    return json.dumps(ret)
