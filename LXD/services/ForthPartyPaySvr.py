import nonebot
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
                r = await response.json()
                print(r)
                if r['code'] == 200:
                    async with aiohttp.ClientSession() as QRsession:
                        async with QRsession.get('https://ppay.mmbbo.cn/api.php/pp/scerweima2?url=' + r['data']['qrcode']) as resp:
                            return base64.b64encode(await resp.read()).decode()
                else:
                    return None

