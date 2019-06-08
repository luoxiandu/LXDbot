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
    if session.state.get('cached'):
        cache = session.get('cache', prompt='您要使用充值前最后一次缓存的订单吗？')
        if cache not in ():
            del session.state['cash']
            del session.state['level']
            del session.state['unlock']
    cash = session.get('cash', prompt='请输入您期望得到的游戏币数额（如果不购买鲨鱼卡请输入0）：')
    session.state['cash'] = cash
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
    redshark = cash // 100000 + 1 if cash != 0 else 0
    level = session.get('level', prompt='请输入您期望更改的级别（如果不购买等级更改请输入0）：')
    session.state['level'] = level
    unlock = session.get('unlock', prompt='您要购买解锁吗？如购买解锁请回复“解锁”，否则输入任意内容继续：')
    session.state['unlock'] = unlock
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
    if total == 0:
        session.finish("您本次下单任何需求都没有，但我也很开心，欢迎再次光顾！")
    gametotal = megalodon * 8000000 + whale * 3500000 + greatwhite * 1250000 + bullshark * 500000 + tigershark * 200000 + redshark * 100000
    msg = "根据您的需求，为您定制的鲨鱼卡方案为：\n巨齿鲨卡%d张，鲸鲨卡%d张，大白鲨卡%d张，牛鲨卡%d张，虎鲨卡%d张，红鲨卡%d张" % (megalodon, whale, greatwhite, bullshark, tigershark, redshark)
    msg += '\n这些鲨鱼卡充值完成后您将获得游戏币' + str(gametotal)
    msg += '\n加上其它需求，您的订单总价格为：' + str(float(total) / 100) + '元，确认下单请回复“确认”，或回复其它内容取消下单。'
    confirm = session.get('confirm', prompt=msg)
    if confirm == '确认':
        result = db.cost(acc, total)
        if result:
            msg = acc + '购买了账号服务：'
            msg += "\n巨齿鲨卡800w：" + str(megalodon) + '张'
            msg += "\n鲸鲨卡350w：" + str(whale) + '张'
            msg += "\n大白鲨卡125w：" + str(greatwhite) + '张'
            msg += "\n牛鲨卡50w：" + str(bullshark) + '张'
            msg += "\n虎鲨卡20w：" + str(tigershark) + '张'
            msg += "\n红鲨卡10w：" + str(redshark) + '张'
            msg += "\n刷级：" + level
            msg += "\n解锁：" + repr(unlock)
            await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
            db.orderGameAccountService(acc, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, total)
            session.finish('已成功下单！猫哥正在火速帮你进行账号服务，请留意他的私聊')
        else:
            want_to_recharge = session.get('want_to_recharge', prompt='您的余额不足，您想马上充值吗？\n请回复“微信”或“支付宝”，或其它内容取消充值')
            if want_to_recharge in ('支付宝', '微信'):
                await session.send('请充值之后重新发送下单指令')
                session.state['cached'] = True
                await call_command(session.bot, session.ctx, name='generalDeposit',
                                   current_arg=want_to_recharge + ' ' + str(float(total) / 100))
            else:
                session.finish('已取消充值')
    else:
        session.finish('您的账号服务订单已取消！')


@bot.server_app.route('/gameservice/getall', methods=['GET'])
async def getGameService():
    return json.dumps(db.getGameAccountService())


@bot.server_app.route('/gameservice/getunfinished', methods=['GET'])
async def getGameServiceUnfinished():
    return json.dumps(db.getGameAccountServiceUnfinished())


@bot.server_app.route('/gameservice/setfinished', methods=['POST'])
async def finishGameService():
    data = await request.form
    id = data['id']
    db.finishGameAccountService(id)
    return json.dumps({'status': 'success'})


@bot.server_app.route('/gameservice/order', methods=['POST'])
async def makeorder():
    data = await request.form
    # noinspection PyBroadException
    try:
        acc = data['username']
        # grplst = await bot.get_group_list()
        # for grp in grplst:
        #     try:
        #         info = await bot.get_group_member_info(group_id=grp['group_id'], user_id=acc)
        #     except ActionFailed:
        #         continue
        #     if info.get('group_id') == grp['group_id']:
        #         grpid = str(info['group_id'])
        grpid = '1'
        megalodon = int(data['megalodon'])
        whale = int(data['whale'])
        greatwhite = int(data['greatwhite'])
        bullshark = int(data['bullshark'])
        tigershark = int(data['tigershark'])
        redshark = int(data['redshark'])
        level = int(data['level'])
        unlock = bool(data['unlock'])
        total = 0
        total += megalodon * int(db.getprice('megalodon_' + grpid))
        total += whale * int(db.getprice('whale_' + grpid))
        total += greatwhite * int(db.getprice('greatwhite_' + grpid))
        total += bullshark * int(db.getprice('bullshark_' + grpid))
        total += tigershark * int(db.getprice('tigershark_' + grpid))
        total += redshark * int(db.getprice('redshark_' + grpid))
        if level != '0':
            total += int(db.getprice('level_' + grpid))
        if unlock:
            total += int(db.getprice('unlock_' + grpid))
        if db.cost(acc, total):
            msg = acc + '购买了账号服务：'
            msg += "\n巨齿鲨卡800w：" + str(megalodon) + '张'
            msg += "\n鲸鲨卡350w：" + str(whale) + '张'
            msg += "\n大白鲨卡125w：" + str(greatwhite) + '张'
            msg += "\n牛鲨卡50w：" + str(bullshark) + '张'
            msg += "\n虎鲨卡20w：" + str(tigershark) + '张'
            msg += "\n红鲨卡10w：" + str(redshark) + '张'
            msg += "\n刷级：" + level
            msg += "\n解锁：" + repr(unlock)
            # await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
            db.orderGameAccountService(acc, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, total)
            return "下单成功！猫哥正在火速帮你进行账号服务，请留意他的私聊。"
        else:
            return "下单失败，您的余额不足，请充值。"
    except Exception as e:
        return "下单失败，请检查您的各项输入是否有误！\n" + e

