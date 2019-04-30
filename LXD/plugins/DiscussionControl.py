from nonebot import on_notice, on_request, NoticeSession, RequestSession, on_command, CommandSession, NoneBot
from nonebot.message import message_preprocessor, Context_T
from nonebot.helpers import send
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB

__plugin_name__ = 'LXD.DiscussionControl'
db = DB()


@on_command('cls', aliases=('清屏',), permission=SUPERUSER, only_to_me=False)
async def cls(session:CommandSession):
    await session.send('开始清屏')
    clswords = '-清屏指令-群主专用-非常拉风-再清两下-保证秩序-遵守群规-不说废话-不发广告-不煽动情绪-不威胁管理-'
    for k in clswords:
        await session.send(k)
    session.finish('清屏完成')
