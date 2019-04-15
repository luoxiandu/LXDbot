from nonebot import on_command, CommandSession
from LXD.services.AlipaySvr import AlipaySvr
from LXD.services.DBSvr import DB

alipay = AlipaySvr()
db = DB()


@on_command('checkAlipay', aliases=('支付宝交易号',), shell_like=True)
async def checkAlipay(session:CommandSession):
    orderid = session.argv[0]
    cache = db.getAlipayTradeNo(orderid)
    if cache:
        if cache['used'] == '0':
            db.deposit(session.ctx['user_id'], cache['amount'])
            db.useAlipayTradeNo(orderid)
            await session.finish(repr(float(cache['amount']) / 100) + '元已经收到，充值成功！')
        else:
            await session.finish('这笔款项已经有人认领过，请换一笔款项进行认领。')
    else:
        result = alipay.checkoderid(orderid, 0)
        if result:
            db.saveAlipayTradeNo({
                'tradeNo': orderid,
                'memo': session.ctx['user_id'],
                'amount': int(result * 100)
            })
            db.useAlipayTradeNo(orderid)
            db.deposit(session.ctx['user_id'], int(result * 100))
            await session.finish(repr(result) + '元已经收到，充值成功！')
        else:
            await session.finish('未查询到款项！请确认钱款已经打入正确的账户。')

