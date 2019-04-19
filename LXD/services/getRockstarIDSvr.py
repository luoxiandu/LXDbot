import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class RockstarIDgetter:
    __browser__ = None

    def __init__(self):
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL'}
        self.__browser__ = webdriver.Chrome(desired_capabilities=caps, executable_path='bin/Chrome/chromedriver.exe')
        self.__browser__.get("https://zh-cn.socialclub.rockstargames.com")
        # logs = [json.loads(log['message'])['message'] for log in self.__browser__.get_log('performance')]
        self.__browser__.implicitly_wait(120)
        avatar = self.__browser__.find_element_by_xpath("//div[@data-ui-name='avatar']")
        if avatar:
            print('登录成功！')
        self.getID('AngeloTheCat')

    def getID(self, username):
        self.__browser__.get("https://zh-cn.socialclub.rockstargames.com/member/%s/" % username)
        self.__browser__.implicitly_wait(10)
        logs = [json.loads(log['message'])['message'] for log in self.__browser__.get_log('performance')]
        with open('har.json', 'w') as fp:
            json.dump(logs, fp)
