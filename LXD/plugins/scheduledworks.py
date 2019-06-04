from LXD.services.DBSvr import DB, SessionkeyManager
from nonebot import get_bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

__plugin_name__ = 'LXD.scheduledworks'
db = DB()
ssmgr = SessionkeyManager()
bot = get_bot()
sched = AsyncIOScheduler()


async def resetvars():
    msg = "今日实时更新注入器使用总结："
    msg += "\n今日登录：" + db.getvar('logincountday') + '次'
    msg += "\n今日注入：" + db.getvar('dllcountday') + '次'
    # await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
    await bot.send_group_msg_rate_limited(group_id=105976356, message=msg)
    db.setvar('dllcountday', 0)
    db.setvar('logincountday', 0)
    return


async def reportinjectorinfo():
    msg = "当前实时更新注入器使用情况如下："
    msg += "\n总登录：" + db.getvar('logincount') + '次'
    msg += "\n今日登录：" + db.getvar('logincountday') + '次'
    msg += "\n总注入：" + db.getvar('dllcount') + '次'
    msg += "\n今日注入：" + db.getvar('dllcountday') + '次'
    msg += "\n当前总在线人数：" + str(db.getonline())
    await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
    # await bot.send_group_msg_rate_limited(group_id=105976356, message=msg)
    return

async def checkonline():
    await ssmgr.chkonline()


sched.add_job(checkonline, 'interval', seconds=5)
sched.add_job(resetvars, 'cron', hour=0, minute=0, second=0)
sched.add_job(reportinjectorinfo, 'cron', minute=0, second=0, hour='*/6')
sched.start()
