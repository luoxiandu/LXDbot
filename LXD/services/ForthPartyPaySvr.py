import nonebot
from quart import request
from aiocqhttp.exceptions import ActionFailed
from LXD.services.DBSvr import DB
import aiohttp
import config
import hashlib
import json
import base64
import time

class ForthPaySvr:
    __db__ = None
    __QQbot__ = nonebot.get_bot()

    def __init__(self):
        self.__db__ = DB()

    async def getPayQRcode(self, price, type, orderuid, goodsname):
        orderid = repr(int(time.time())) + orderuid
        postdata = {
            'identification': config.pay_identification,
            'price': price,
            'type': type,
            'notify_url': config.pay_notify_url,
            'return_url': config.pay_return_url,
            'orderid': orderid,
            'orderuid': orderuid,
            'goodsname': goodsname,
        }
        keystr = goodsname + config.pay_identification + config.pay_notify_url + orderid + orderuid + price + config.pay_return_url + config.pay_token + type
        postdata['key'] = hashlib.md5(keystr.encode('utf-8')).hexdigest()
        async with aiohttp.ClientSession() as session:
            async with session.post('https://ppay.mmbbo.cn/index.php?s=/api/pp/index_show.html', data=postdata) as response:
                r = json.load(response)
                if r['code'] == 200:
                    async with aiohttp.ClientSession() as QRsession:
                        async with QRsession.get('https://ppay.mmbbo.cn/api.php/pp/scerweima2?url=' + r['data']['qrcode']) as resp:
                            return base64.b64encode(resp.read())
                else:
                    return None

    @__QQbot__.server_app.route('/020pay_notice', methods=['POST'])
    async def notify_handler_020(self):
        data = await request.form
        kstr = data['actual_price'] + data['bill_no'] + data['orderid'] + data['orderuid'] + data[
            'price'] + config.pay_token
        if hashlib.md5(kstr.encode('utf-8')).hexdigest() == data['key']:
            self.__db__.saveForthPartyOrder(data)
            self.__db__.deposit(data['orderuid'], int(data['price']))
            try:
                await self.__QQbot__.send_private_msg_rate_limited(user_id=int(data['orderuid']), message='您的' + repr(
                    float(data['price']) / 100) + '元充值已到账！')
            except ActionFailed as e:
                print('酷QHTTP插件错误，返回值：' + repr(e.retcode))
            return
        else:
            return 'Token Validation Failed.'

