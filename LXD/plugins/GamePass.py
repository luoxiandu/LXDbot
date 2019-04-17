from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB

db = DB()


@on_command('getGamePass', aliases=('购买账号', '账号购买', '购买黑号', '黑号购买'), only_to_me=False)
async def getGamePass(session:CommandSession):
    account = session.ctx['user_id']
    price = db.getprice('GamePass')
    if db.checkgamepass() == 0:
        session.finish('目前没有库存，请等待上货。')
    alert = ("[CQ:at,qq={%d}]" % account) + "要购买价值" + str(float(price) / 100) + "的游戏账号，是否确定购买？"
    ensure = session.get('ensure_to_buy', prompt=alert)
    if ensure not in ('是', '确定', '购买'):
        session.finish('已取消购买。')
    result = db.cost(account, price)
    if result:
        gp = db.getgamepass()
        strgp = '您购买的账号信息如下：'
        strgp += '\n邮箱：' + gp['email']
        strgp += '\n邮箱密码：' + gp['emailpassword']
        strgp += '\nSteam账号：' + gp['steam']
        strgp += '\nSteam密码：' + gp['steampassword']
        strgp += '\n序列号：' + gp['key']
        session.finish(strgp, ensure_private=True)
    else:
        session.finish('扣款失败，请查询余额！')


@on_command('addGamePass', aliases=('添加账号', '账号上货'), privileged=SUPERUSER)
async def addGamePass(session:CommandSession):
    stripped_arg = session.current_arg_text.strip()
    lines = stripped_arg.split('\n')
    gpList = []
    errcount = 0
    for line in lines:
        gp = line.split('----')
        if len(gp) != 5:
            errcount += 1
            continue
        gpList.append({
            'email': gp[0],
            'emailpassword': gp[1],
            'steam': gp[2],
            'steampassword': gp[3],
            'key': gp[4],
        })
    db.addgamepass(gpList)
    session.finish("上货完成！共有数据" + str(len(lines)) + "行，成功上货" + str(len(gpList)) + "个，未识别行数为" + repr(errcount))


@on_command('checkGamePass', aliases=('查询账号余量', '查询黑号余量'), privileged=SUPERUSER)
async def checkGamePass(session:CommandSession):
    session.finish("当前账号余量：" + repr(db.checkgamepass()))


@on_command('setGamePassPrice', aliases=('设置黑号价格', '设置账号价格'), privileged=SUPERUSER)
async def setGamePassPrice(session:CommandSession):
    price = eval(session.current_arg_text.strip())
    db.setprice('GamePass', int(price * 100))
    session.finish('设置成功完成')


@on_command('getGamePassPrice', aliases=('查询黑号价格', '查询账号价格'), privileged=SUPERUSER)
async def getGamePassPrice(session:CommandSession):
    session.finish("当前账号价格：" + repr(float(db.getprice('GamePass')) / 100))

