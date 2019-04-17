import nonebot
import config
from quart import request
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import ActionFailed
from LXD.services.ForthPartyPaySvr import ForthPaySvr
from LXD.services.DBSvr import DB
from sqlite3 import IntegrityError
from nonebot.permission import SUPERUSER
import hashlib

pay = ForthPaySvr()
db = DB()
bot = nonebot.get_bot()


@on_command('generalDeposit', aliases=('充值', '快速充值'), shell_like=True)
async def generalDeposit(session:CommandSession):
    if len(session.argv) == 2:
        price = int(eval(session.argv[1]) * 100)
        if session.argv[0] == '支付宝':
            qrcode = await pay.getPayQRcode(price=repr(price), type='2', orderuid=repr(session.ctx['user_id']), goodsname='支付宝充值')
            if qrcode:
                msg = {
                    'type': 'image',
                    'data': {
                        'file': 'base64://' + qrcode
                    }
                }
            else:
                msg = '获取支付宝二维码错误，请重试或联系群主。'
        elif session.argv[0] == '微信':
            qrcode = await pay.getPayQRcode(price=repr(price), type='1', orderuid=repr(session.ctx['user_id']), goodsname='微信充值')
            if qrcode:
                msg = {
                    'type': 'image',
                    'data': {
                        'file': 'base64://' + qrcode
                    }
                }
            else:
                msg = '获取微信二维码错误，请重试或联系群主。'
        else:
            msg = '快速充值用法：发送 充值 微信/支付宝 金额'
        await session.send(msg)
    else:
        await session.send('快速充值用法：发送 充值 微信/支付宝 金额')


@on_command('generalDeposit', aliases=('补单',), privileged=SUPERUSER, shell_like=True)
async def generalDepost(session:CommandSession):
    pass


@on_command('changeSuccessString', aliases=('切换手续费耍赖状态',), privileged=SUPERUSER)
async def changeSuccessString(session:CommandSession):
    success_str = db.getvar('020success')
    if success_str == 'success':
        db.setvar('020success', 'surprise, motherfucker!')
        await session.send('成功切换为手续费耍赖状态！')
    else:
        db.setvar('020success', 'success')
        await session.send('成功切换为手续费不耍赖状态！')


@on_command('getSuccessString', aliases=('查询手续费耍赖状态',), privileged=SUPERUSER)
async def getSuccessString(session:CommandSession):
    success_str = db.getvar('020success')
    if success_str == 'success':
        await session.send('现在是手续费不耍赖状态！')
    else:
        await session.send('现在是手续费耍赖状态！请注意别被察觉！')


@bot.server_app.route('/020pay_notice', methods=['POST'])
async def notify_handler_020():
    success_str = db.getvar('020success')
    data = await request.form
    kstr = data['actual_price'] + data['bill_no'] + data['orderid'] + data['orderuid'] + data[
        'price'] + config.pay_token
    if hashlib.md5(kstr.encode('utf-8')).hexdigest() == data['key']:
        try:
            db.saveForthPartyOrder(data)
        except IntegrityError:
            return success_str
        db.deposit(data['orderuid'], int(data['actual_price']))
        try:
            await bot.send_private_msg_rate_limited(user_id=int(data['orderuid']), message='您的' + repr(
                float(data['actual_price']) / 100) + '元充值已到账！')
        except ActionFailed as e:
            print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
        return success_str
    else:
        return 'Token Validation Failed.'
