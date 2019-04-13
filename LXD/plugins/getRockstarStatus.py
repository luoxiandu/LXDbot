from nonebot import on_command, CommandSession
import json, urllib.request


@on_command('getRockstarStatus', aliases=('服务器状态', 'R星服务器状态', '游戏服务器状态'), only_to_me=False)
async def getRockstarStatus(session:CommandSession):
    result = json.loads(urllib.request.urlopen("https://support.rockstargames.com/services/status.json?tz=Asia/Shanghai").read())
    try:
        GTAstatus = {}
        SCstatus = ''
        for service in result['statuses']:
            if service['tag'] == 'gtao':
                for platform in service['services_platforms']:
                    GTAstatus[platform['name']] = '服务正常' if platform['service_status_id'] == 1 else '暂不可用，Rockstar内部错误代码为' + platform['service_status_id']
            if service['tag'] == 'sc':
                SCstatus = '服务正常' if service['services_platforms'][0]['service_status_id'] == 1 else '暂不可用，Rockstar内部错误代码为' + service['services_platforms'][0]['service_status_id']
    except KeyError:
        await session.send("查询失败，请重试！")
        return
    rstr = "根据Rockstar官方通报，目前GTA Online各平台服务器状态如下：\n"
    for platform in GTAstatus:
        rstr += platform + " 平台：" + GTAstatus[platform] + "\n"
    rstr += 'Rockstar Social Club 服务状态：' + SCstatus
    await session.send(rstr)