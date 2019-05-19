import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import json

__plugin_name__ = 'LXD.GameAccountService'
db = DB()
bot = nonebot.get_bot()


@on_command('buygameservice', aliases=('购买账号服务', ), only_to_me=False)
def buygameservice(session:CommandSession):
    cash = session.get('cash', prompt='请输入您期望得到的游戏币数额，如果不购买鲨鱼卡请输入0：')
    cash = int(cash)
    if not cash == 0:
        megalodon = cash // 8000000
        cash -= megalodon * 8000000
        whale = cash // 3500000
        cash -= whale * 3500000
        greatwhite = cash // 1250000
        cash -= greatwhite * 1250000
        bullshark = cash // 500000
        cash -= bullshark * 500000
        tigershark = cash // 200000
        cash -= tigershark * 200000
        redshark = cash // 100000
        session.send("根据您的需求，为您定制方案：巨齿鲨卡%d张，鲸鲨卡%d张，大白鲨卡%d张，牛鲨卡%d张，虎鲨卡%d张，红鲨卡%d张" % (megalodon, whale, greatwhite, bullshark, tigershark, redshark))
    level = session.get('level', prompt='请输入您期望更改的级别，如果不购买等级更改请输入0')
    unlock = session.get('unlock', prompt='您要购买解锁吗？')
