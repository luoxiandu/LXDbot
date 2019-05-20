from nonebot import on_notice, on_request, NoticeSession, RequestSession
from nonebot.log import logger
from LXD.services.DBSvr import DB

__plugin_name__ = 'LXD.noticeHelper'
db = DB()

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
    await session.send('欢迎新朋友！洛仙都商店随时恭候您的光临~请私聊我设置密码，在群文件下载注入器，开始您的仙境之旅吧！有问题及需要帮助请回复“主菜单”查看更多功能和提示。')
    await session.send('警告：如果有人加您的好友并向您兜售游戏账号或游戏服务，基本都是来路不正，任何保证都没有的，本群对于这种私下兜售产生的纠纷概不负责！也请萌新明辨是非，不要惹上这种纠纷。')

@on_notice('group_decrease')
async def group_decrease(session:NoticeSession):
    db.deleteaccount(session.ctx['user_id'])
    await session.send(repr(session.ctx['user_id']) + '退群了，他的账号已经被删除，无法使用外挂下载注入系统，并且账户里的余额也被清零了。大家千万不要学他！')
