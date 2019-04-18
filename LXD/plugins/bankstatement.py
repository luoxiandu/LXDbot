from nonebot import on_command, CommandSession
from nonebot.command import call_command
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB

db = DB()


@on_command('addStatement', aliases=('记账',), privileged=SUPERUSER, only_to_me=False, shell_like=True)
async def addStatement(session:CommandSession):
    if len(session.argv) == 2:
        amount = int(eval(session.argv[0]) * 100)
        memo = session.argv[1]
        db.saveStatement(amount, memo)
        bank = int(db.getvar('Bank'))
        bank += amount
        db.setvar('Bank', bank)
        session.finish('记账成功！账目 ' + memo + ' 收入/支出' + session.argv[0] + '元，当前群余额为' + repr(float(bank) / 100))
    else:
        session.finish('用法：记账 金额（带正负） 账目名称')


@on_command('checkBank', aliases=('查询群费',), privileged=SUPERUSER, only_to_me=False)
async def checkBank(session:CommandSession):
    session.finish('当前群费余额为：' + repr(float(db.getvar('Bank')) / 100) + '元')
