from LXD.services.DBSvr import DB, SessionkeyManager
from nonebot import get_bot
import nonebot

__plugin_name__ = 'LXD.scheduledworks'
bot = get_bot()


@nonebot.scheduler.scheduled_job('cron', hour=0, minute=0, second=0)
async def resetvars():
    db = DB()
    msg = "今日实时更新注入器使用总结："
    msg += "\n今日登录：" + db.getvar('logincountday') + '次'
    msg += "\n今日注入：" + db.getvar('dllcountday') + '次'
    # await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
    await bot.send_group_msg_rate_limited(group_id=667556362, message=msg)
    db.setvar('dllcountday', 0)
    db.setvar('logincountday', 0)
    db.statistics_resetday()
    del db
    return


@nonebot.scheduler.scheduled_job('cron', minute=0, second=0, hour='*/6')
async def reportinjectorinfo():
    db = DB()
    ssmgr = SessionkeyManager()
    msg = "当前实时更新注入器使用情况如下："
    msg += "\n总登录：" + db.getvar('logincount') + '次'
    msg += "\n今日登录：" + db.getvar('logincountday') + '次'
    msg += "\n总注入：" + db.getvar('dllcount') + '次'
    msg += "\n今日注入：" + db.getvar('dllcountday') + '次'
    msg += "\n当前总在线人数：" + str(ssmgr.getonline())
    await bot.send_group_msg_rate_limited(group_id=869494996, message=msg)
    # await bot.send_group_msg_rate_limited(group_id=667556362, message=msg)
    del db
    del ssmgr
    return


@nonebot.scheduler.scheduled_job('interval', seconds=5)
async def checkonline():
    ssmgr = SessionkeyManager()
    await ssmgr.chkonline()
    del ssmgr
