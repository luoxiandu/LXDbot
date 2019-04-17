import nonebot
from aiocqhttp.exceptions import ActionFailed
from LXD.services.DBSvr import DB
from aiohttp import web
import config
import hashlib

db = DB()
QQbot = nonebot.get_bot()


async def notify_handler_020(request):
    data = await request.post()
    kstr = data['actual_price'] + data['bill_no'] + data['orderid'] + data['orderuid'] + data[
        'price'] + config.pay_token
    if hashlib.md5(kstr.encode('utf-8')).hexdigest() == data['key']:
        db.saveForthPartyOrder(data)
        db.deposit(data['orderuid'], int(data['price']))
        try:
            await QQbot.send_private_msg_rate_limited(user_id=int(data['orderuid']), message='您的' + repr(
                float(data['price']) / 100) + '元充值已到账！')
        except ActionFailed as e:
            print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
    else:
        return web.Response(text='Token Validation Failed.')

if __name__ == '__main__':
    webserver = web.Application()
    webserver.add_routes([web.post('/020pay', notify_handler_020)])
    web.run_app(webserver)