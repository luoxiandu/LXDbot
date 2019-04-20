from nonebot import on_notice, on_request, NoticeSession, RequestSession
from nonebot.log import logger

__plugin_name__ = 'LXD.noticeHelper'


@on_notice
async def _(session: NoticeSession):
    logger.info('有新的通知事件：%s', session.ctx)


@on_request
async def _(session: RequestSession):
    logger.info('有新的请求事件：%s', session.ctx)

# 将函数注册为群成员增加通知处理器
@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    await session.send('欢迎新朋友～')
