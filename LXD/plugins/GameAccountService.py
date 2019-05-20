import nonebot
from quart import request
from nonebot import on_command, CommandSession
from nonebot.command import call_command
from nonebot.permission import SUPERUSER
from aiocqhttp.exceptions import ActionFailed
from LXD.services.DBSvr import DB
import json

__plugin_name__ = 'LXD.GameAccountService'
db = DB()
bot = nonebot.get_bot()


@on_command('buygameservice', aliases=('购买账号服务', '下单'), only_to_me=False)
async def buygameservice(session:CommandSession):
    acc = str(session.ctx['user_id'])
    try:
        grpid = str(session.ctx['group_id'])
    except KeyError:
        grplst = await bot.get_group_list()
        for grp in grplst:
            try:
                info = await bot.get_group_member_info(group_id=grp['group_id'], user_id=acc)
            except ActionFailed:
                continue
            if info.get('group_id') == grp['group_id']:
                grpid = str(info['group_id'])
    cash = session.get('cash', prompt='请输入您期望得到的游戏币数额（如果不购买鲨鱼卡请输入0）：')
    cash = int(cash)
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
    await session.send("根据您的需求，为您定制方案：巨齿鲨卡%d张，鲸鲨卡%d张，大白鲨卡%d张，牛鲨卡%d张，虎鲨卡%d张，红鲨卡%d张" % (megalodon, whale, greatwhite, bullshark, tigershark, redshark))
    level = session.get('level', prompt='请输入您期望更改的级别（如果不购买等级更改请输入0）：')
    unlock = session.get('unlock', prompt='您要购买解锁吗？如购买解锁请回复“解锁”，否则输入任意内容继续：')
    total = 0
    total += megalodon * int(db.getprice('megalodon_' + grpid))
    total += whale * int(db.getprice('whale_' + grpid))
    total += greatwhite * int(db.getprice('greatwhite_' + grpid))
    total += bullshark * int(db.getprice('bullshark_' + grpid))
    total += tigershark * int(db.getprice('tigershark_' + grpid))
    total += redshark * int(db.getprice('redshark_' + grpid))
    if level != '0':
        total += int(db.getprice('level_' + grpid))
    if unlock == '解锁':
        unlock = True
        total += int(db.getprice('unlock_' + grpid))
    else:
        unlock = False
    confirm = session.get('confirm', prompt='您的订单总价格为：' + str(float(total) / 100) + '元，确认下单请回复“确认”，或回复其它内容取消下单。')
    if confirm == '确认':
        result = db.cost(acc, total)
        if result:
            msg = acc + '购买了账号服务：'
            msg += "\n巨齿鲨卡：" + str(megalodon) + '张'
            msg += "\n鲸鲨卡：" + str(whale) + '张'
            msg += "\n大白鲨卡：" + str(greatwhite) + '张'
            msg += "\n牛鲨卡：" + str(bullshark) + '张'
            msg += "\n虎鲨卡：" + str(tigershark) + '张'
            msg += "\n红鲨卡：" + str(redshark) + '张'
            msg += "\n刷级：" + level
            msg += "\n解锁：" + repr(unlock)
            await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
            db.orderGameAccountService(acc, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, total)
            session.finish('已成功下单！猫哥正在火速帮你进行账号服务，请留意他的私聊')
        else:
            want_to_recharge = session.get('want_to_recharge', prompt='您的余额不足，您想马上充值吗？\n请回复“微信”或“支付宝”，或其它内容取消充值')
            if want_to_recharge in ('支付宝', '微信'):
                await session.send('请充值之后重新发送下单指令')
                await call_command(session.bot, session.ctx, name='generalDeposit',
                                   current_arg=want_to_recharge + ' ' + str(float(total) / 100))
            else:
                session.finish('已取消充值')
