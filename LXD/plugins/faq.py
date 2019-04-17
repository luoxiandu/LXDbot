from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from LXD.services.DBSvr import DB
import re

db = DB()


@on_command('ask', aliases=('问',''), only_to_me=False)
async def ask(session:CommandSession):
    question = session.current_arg
    answer = db.getvar('question_' + question)
    session.finish(answer)


@on_command('addQuestion', aliases=('设置问题', '设问'), privileged=SUPERUSER)
async def addQuestion(session:CommandSession):
    c = re.split(r'(#[^#]+#)(.+)', session.current_arg, flags=re.M | re.S)
    question = c[1].strip('#')
    answer = c[2].strip()
    db.setvar('question_' + question, answer)
    session.finish('问题' + question + '设置成功！')
