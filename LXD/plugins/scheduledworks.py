from LXD.services.DBSvr import DB
from apscheduler.schedulers.asyncio import AsyncIOScheduler

db = DB()
sched = AsyncIOScheduler()


async def resetvars():
    db.setvar('dllcountday', 0)
    db.setvar('logincountday', 0)
    return


sched.add_job(resetvars, 'cron', hour=0, minute=0, second=0)
sched.start()
