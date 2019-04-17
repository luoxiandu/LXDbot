from nonebot import on_command, CommandSession
from LXD.services.ForthPartyPaySvr import ForthPaySvr
from LXD.services.DBSvr import DB
from nonebot.permission import SUPERUSER
from importlib import reload

pay = ForthPaySvr()
db = DB()


@on_command('generalDeposit', aliases=('充值', '快速充值'), shell_like=True)
async def generalDeposit(session:CommandSession):
    if len(session.argv) == 2:
        price = int(eval(session.argv[1]) * 100)
        if session.argv[0] == '支付宝':
            qrcode = await pay.getPayQRcode(price=price, type=2, orderuid=session.ctx['user_id'], goodsname='支付宝充值')
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + qrcode
                }
            }
        elif session.argv[0] == '微信':
            qrcode = await pay.getPayQRcode(price=price, type=1, orderuid=session.ctx['user_id'], goodsname='微信充值')
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + qrcode
                }
            }
        else:
            msg = '快速充值用法：发送 充值 微信/支付宝 金额'
        await session.send(msg)
    else:
        await session.send('快速充值用法：发送 充值 微信/支付宝 金额')