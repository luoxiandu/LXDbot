from nonebot import on_command, CommandSession
from LXD.services.AlipaySvr import AlipaySvr
from LXD.services.DBSvr import DB

alipay = AlipaySvr()
db = DB()

@on_command('checkAlipay', aliases=('支付宝交易号',), shell_like=True)
async def checkAlipay(session:CommandSession):
    result = alipay.checkoderid(session.argv[0], 0)
    if result:
        db.deposit(session.ctx['user_id'], int(result * 100))
        session.finish(repr(result) + '元已经收到，充值成功！')
    else:
        session.finish('未查询到款项！请确认钱款已经打入正确的账户。')