import nonebot
import config
from quart import request
from nonebot import on_command, CommandSession
from nonebot.log import logger
from aiocqhttp.exceptions import ActionFailed
from LXD.services.ForthPartyPaySvr import ForthPaySvr
from LXD.services.DBSvr import DB
from sqlite3 import IntegrityError
from nonebot.permission import SUPERUSER
import hashlib

__plugin_name__ = 'LXD.ForthPartyPay'
pay = ForthPaySvr()
db = DB()
bot = nonebot.get_bot()


@on_command('generalDeposit', aliases=('充值', '快速充值', 'cz', 'CZ'), shell_like=True, only_to_me=False)
async def generalDeposit(session:CommandSession):
    if len(session.argv) == 2:
        price = int(eval(session.argv[1]) * 100)
        if session.argv[0] in ('支付宝', 'zfb', 'ZFB'):
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
        elif session.argv[0] in ('微信', 'wx', 'WX'):
            qrcode = await pay.getPayQRcode(price=repr(price), type='1', orderuid=repr(session.ctx['user_id']), goodsname='微信充值')
            if qrcode:
                msg = {
                    'type': 'image',
                    'data': {
                        'file': 'base64://' + qrcode
                    }
                }
                await bot.send_group_msg_rate_limited(group_id=869494996, message=str(session.ctx['user_id']) + '获取了' + session.argv[0] + repr(price) + '元二维码')
                logger.info(str(session.ctx['user_id']) + '获取了' + session.argv[0] + repr(price) + '元二维码')
            else:
                msg = '获取微信二维码错误，请重试或联系群主。'
        else:
            msg = '快速充值用法：发送 充值 微信/支付宝 金额'
        session.finish(msg)
    else:
        session.finish('充值命令用法：请向我发送“充值 微信/支付宝 金额”，例如您想用微信充值100元，请发送“充值 微信 100”')


@on_command('generalManualDeposit', aliases=('手动充值', 'sdcz', 'SDCZ'), permission=SUPERUSER, shell_like=True, only_to_me=False)
async def generalManualDeposit(session:CommandSession):
    account = session.argv[0]
    amount = int(float(session.argv[1]) * 100)
    db.deposit(account, amount)
    try:
        await bot.send_private_msg_rate_limited(user_id=int(account), message='您的' + session.argv[1] + '元充值已到账！')
    except ActionFailed as e:
        print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
    session.finish('成功为' + session.argv[0] + '充值' + session.argv[1] + '元！')


@on_command('generalManualCost', aliases=('手动扣款', 'sdkk', 'SDKK'), permission=SUPERUSER, shell_like=True, only_to_me=False)
async def generalManualCost(session:CommandSession):
    account = session.argv[0]
    item = session.argv[1]
    amount = int(float(session.argv[2]) * 100)
    if db.cost(account, amount):
        try:
            await bot.send_private_msg_rate_limited(user_id=int(account), message='您已成功购买' + item + '！付款' + session.argv[2] + '元。')
        except ActionFailed as e:
            print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
        session.finish('成功对' + session.argv[0] + '扣款' + session.argv[2] + '元！')
    else:
        session.finish(account + '的余额不足，请提醒他充值或手动收款')


@on_command('changeSuccessString', aliases=('切换手续费耍赖状态', 'qhsxfsl', 'QHSXFSL'), permission=SUPERUSER, only_to_me=False)
async def changeSuccessString(session:CommandSession):
    success_str = db.getvar('020success')
    if success_str == 'success':
        db.setvar('020success', 'Token Validation Failed.')
        session.finish('成功切换为手续费耍赖状态！')
    else:
        db.setvar('020success', 'success')
        session.finish('成功切换为手续费不耍赖状态！')


@on_command('getSuccessString', aliases=('查询手续费耍赖状态', 'cxsxfsl', 'CXSXFSL'), permission=SUPERUSER, only_to_me=False)
async def getSuccessString(session:CommandSession):
    success_str = db.getvar('020success')
    if success_str == 'success':
        session.finish('现在是手续费不耍赖状态！')
    else:
        session.finish('现在是手续费耍赖状态！请注意别被察觉！')


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
        db.saveStatement(int(data['actual_price']), '自动记账-充值收入' + data['orderuid'])
        bank = int(db.getvar('Bank'))
        bank += int(data['actual_price'])
        db.setvar('Bank', bank)
        try:
            await bot.send_group_msg_rate_limited(group_id=869494996, message='用户充值自动入账：' +
                data['orderuid'] + '充值' + repr(float(data['actual_price']) / 100) + '元')
            await bot.send_private_msg_rate_limited(user_id=int(data['orderuid']), message='您的' + repr(
                float(data['actual_price']) / 100) + '元充值已到账！')
        except ActionFailed as e:
            print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
        return success_str
    else:
        return 'Token Validation Failed.'


@bot.server_app.route('/020pay_getQRcode', methods=['POST'])
async def LXDClientGetQRcode():
    data = await request.form
    try:
        price = int(float(data['price']) * 100)
    except ValueError:
        return "<h1>金额输入错误</h1>"
    if data['paytype'] == '支付宝':
        paytype = '2'
    elif data['paytype'] == '微信':
        paytype = '1'
    else:
        return "<h1>支付方式选择错误</h1>"
    uid = data['username']
    return "<img src=\"data:image/png;base64," + await pay.getPayQRcode(price=repr(price), type=paytype, orderuid=uid, goodsname='客户端充值') + "\" />"
