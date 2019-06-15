import nonebot
from LXD.services.DBSvr import DB
import json

__plugin_name__ = 'LXD.Advertisement'
db = DB()
bot = nonebot.get_bot()


@bot.server_app.route('/getadv',methods=['GET'])
async def getadv():
    return json.dumps(db.getAdvertisements())