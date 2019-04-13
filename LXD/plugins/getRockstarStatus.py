from nonebot import on_command, CommandSession
import json, urllib.request


@on_command('getRockstarStatus', aliases=('服务器状态', 'R星服务器状态', '游戏服务器状态'))
async def getRockstarStatus(session:CommandSession):
    result = json.loads(urllib.request.urlopen("https://support.rockstargames.com/services/status.json?tz=Asia/Shanghai").read())
    try:
        status = {}
        for service in result['statuses']:
            if service['tag'] == 'gtao':
                for platform in service['services_platforms']:
                    status[platform['name']] = '服务正常' if platform['service_status_id'] == 1 else '暂不可用，Rockstar内部错误代码为' + platform['service_status_id']
    except KeyError:
        await session.send("查询失败，请重试！")
        return
    rstr = "根据Rockstar官方通报，目前GTA Online各平台服务器状态如下：\n"
    for platform in status:
        rstr += platform + " 平台：" + status[platform] + "\n"
    await session.send(rstr)