from nonebot import on_command, CommandSession
from nonebot.command import call_command
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import time

__plugin_name__ = 'LXD.bankstatement'
db = DB()


@on_command('addStatement', aliases=('记账',), permission=SUPERUSER, only_to_me=False, shell_like=True)
async def addStatement(session:CommandSession):
    if len(session.argv) == 2:
        amount = int(eval(session.argv[0]) * 100)
        memo = session.argv[1]
        db.saveStatement(amount, memo)
        bank = int(db.getvar('Bank'))
        bank += amount
        db.setvar('Bank', bank)
        session.finish('记账成功！账目 ' + memo + ' 收入/支出' + session.argv[0] + '元，当前群余额为' + repr(float(bank) / 100) + '元。')
    else:
        session.finish('用法：记账 金额（带正负） 账目名称')


@on_command('checkBank', aliases=('查询群费',), permission=SUPERUSER, only_to_me=False)
async def checkBank(session:CommandSession):
    session.finish('当前群费余额为：' + repr(float(db.getvar('Bank')) / 100) + '元')


@on_command('getBankStatementByInterval', aliases=('查询流水', '查账'), permission=SUPERUSER, only_to_me=False)
async def getBankStatementByInterval(session:CommandSession):
    start = session.get('start', prompt='请输入您要查账的起始日期，格式：年-月-日')
    end = session.get('end', prompt='请输入您要查账的结束日期，格式：年-月-日')
    start = time.mktime(time.strptime(start, '%Y-%m-%d'))
    end = time.mktime(time.strptime(end, '%Y-%m-%d'))
    msg = '您选择的区间内的账目如下：'
    r = db.getStatementByInterval(start, end)
    for line in r['details']:
        msg += '\n|序号：'+ line['rowid'] + ' | ' + line['amount'] + '元 | ' + line['memo']
    msg += '\n区间净收入：' + repr(float(r['total_amount']) / 100) + '元'
    session.finish(msg)
