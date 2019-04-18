from nonebot import on_command, CommandSession
from LXD.services.AlipaySvr import AlipaySvr
from LXD.services.DBSvr import DB
from nonebot.permission import SUPERUSER
from importlib import reload

__plugin_name__ = '支付宝网页端收款系统（已停用）'
# alipay = AlipaySvr()
alipay = None
db = DB()


@on_command('checkAlipay', aliases=('支付宝交易号',), shell_like=True)
async def checkAlipay(session:CommandSession):
    orderid = session.argv[0]
    cache = db.getAlipayTradeNo(orderid)
    if cache:
        if not cache['used']:
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


@on_command('reboot', aliases=('重启支付宝模块',), privileged=SUPERUSER)
async def reboot(session:CommandSession):
    reload(AlipaySvr)
    await session.finish('模块重新加载完毕')


@on_command('manualAlipayCheck', aliases=('手动支付宝充值',), privileged=SUPERUSER, shell_like=True)
async def manualAlipayCheck(session:CommandSession):
    try:
        user = session.argv[0]
    except KeyError:
        await session.send('第一个参数是被充值QQ号！')
        return
    try:
        tradeNo = session.argv[1]
    except KeyError:
        await session.send('第二个参数是支付宝流水号！')
        return
    try:
        amount = session.argv[2]
    except KeyError:
        await session.send('第三个参数是金额！')
        return
    db.saveAlipayTradeNo({
        'tradeNo': tradeNo,
        'memo': '#手动充值#' + user,
        'amount': int(float(amount) * 100)
    })
    db.useAlipayTradeNo(tradeNo)
    db.deposit(user, int(float(amount) * 100))
    await session.finish('充值完毕！为用户' + user + '充值' + amount)


@on_command('refreshBrowser', aliases=('刷新支付宝页面',), privileged=SUPERUSER)
async def refreshBrowser(session:CommandSession):
    alipay.browser.refresh()
    scrshot = alipay.browser.get_screenshot_as_base64()
    msg = {
        'type': 'image',
        'data': {
            'file': 'base64://' + scrshot
        }
    }
    await session.send(msg)

