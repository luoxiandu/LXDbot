from nonebot import on_notice, on_request, on_command, NoticeSession, RequestSession, CommandSession
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from LXD.services.DBSvr import DB, SessionkeyManager
from nonebot import scheduler
import nonebot
import config
import datetime

__plugin_name__ = 'LXD.noticeHelper'
db = DB()
bot = nonebot.get_bot()
ssmgr = SessionkeyManager()

# @on_notice
# async def onNotice(session: NoticeSession):
#     logger.info('有新的通知事件：%s', session.ctx)
#
#
# @on_request
# async def onRequest(session: RequestSession):
#     logger.info('有新的请求事件：%s', session.ctx)

# 将函数注册为群成员增加通知处理器
@on_notice('group_increase')
async def group_increase(session: NoticeSession):
    # 发送欢迎消息
    grpid = repr(session.ctx['group_id'])
    welcome = db.getvar('welcome_' + grpid)
    warning = db.getvar('warning_' + grpid)
    await session.send(welcome)
    await session.send(warning)
    if grpid == '105976356':
        scheduler.add_job(kick25boy, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=360), args=[str(session.ctx['user_id'])], id=str(session.ctx['user_id']), replace_existing=True)
    # await session.send('欢迎新朋友！洛仙都商店随时恭候您的光临~请私聊我设置密码，在群文件下载注入器，开始您的仙境之旅吧！有问题及需要帮助请回复“主菜单”查看更多功能和提示。')
    # await session.send('警告：如果有人加您的好友并向您兜售游戏账号或游戏服务，基本都是来路不正，任何保证都没有的，本群对于这种私下兜售产生的纠纷概不负责！也请萌新明辨是非，不要惹上这种纠纷。')


async def kick25boy(acc):
    if not db.exist_account(acc):
        await bot.set_group_kick_rate_limited(group_id='105976356', user_id=acc, reject_add_request=True)
        await bot.send_group_msg_rate_limited(group_id=config.notice_group, message=acc + '超时未付费已被自动踢出群')
        logger.info(acc + '超时未付费已被自动踢出群')


@on_notice('group_decrease')
async def group_decrease(session: NoticeSession):
    ssmgr.clearSessionkey(session.ctx['user_id'])
    db.deleteaccount(session.ctx['user_id'])
    decreasewarning = db.getvar('decrease_' + repr(session.ctx['group_id']))
    decreasewarning = decreasewarning.replace('#id#', repr(session.ctx['user_id']))
    await session.send(decreasewarning)
    # await session.send(repr(session.ctx['user_id']) + '退群了，他的账号已经被删除，无法使用外挂下载注入系统，并且账户里的余额也被清零了。大家千万不要学他！')


@on_command('setwelcome', aliases=('设置进群提示语', ), permission=SUPERUSER, only_to_me=False)
def setwelcome(session: CommandSession):
    grpid = session.get('grpid', prompt='请输入要设置进群提示语的群号')
    welcome = session.get('welcome', prompt='请输入欢迎语')
    warning = session.get('warning', prompt='请输入警示语')
    db.setvar('welcome_' + grpid, welcome)
    db.setvar('warning_' + grpid, warning)
    session.finish('设置成功！')


@on_command('setdecrease', aliases=('设置退群提示语', ), permission=SUPERUSER, only_to_me=False)
def setwelcome(session: CommandSession):
    grpid = session.get('grpid', prompt='请输入要设置退群提示语的群号')
    decreasewarning = session.get('welcome', prompt='请输入退群提示语，#id#代表退群者QQ号')
    db.setvar('decrease_' + grpid, decreasewarning)
    session.finish('设置成功！')
