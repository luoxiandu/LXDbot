from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import re

__plugin_name__ = 'LXD.faq'
db = DB()


@on_command('ask', aliases=('问',), only_to_me=False)
async def ask(session:CommandSession):
    question = session.current_arg
    answer = db.getvar('question_' + question)
    if answer:
        session.finish(answer)
    else:
        answer = db.getvar('question_private_' + question)
        if answer:
            await session.send(answer, ensure_private=True)
            session.finish()
    session.finish('没有找到您问的问题 ' + question + ' 哦')


@on_command('addQuestion', aliases=('设置问题', '设问'), permission=SUPERUSER)
async def addQuestion(session:CommandSession):
    c = re.split(r'(#[^#]+#)(.+)', session.current_arg, flags=re.M | re.S)
    question = c[1].strip('#')
    answer = c[2].strip()
    db.setvar('question_' + question, answer)
    session.finish('问题' + question + '设置成功！')


@on_command('addPrivateQuestion', aliases=('设置私密问题', '私密设问'), permission=SUPERUSER)
async def addPrivateQuestion(session:CommandSession):
    c = re.split(r'(#[^#]+#)(.+)', session.current_arg, flags=re.M | re.S)
    question = c[1].strip('#')
    answer = c[2].strip()
    db.setvar('question_private_' + question, answer)
    session.finish('问题' + question + '设置成功！')
