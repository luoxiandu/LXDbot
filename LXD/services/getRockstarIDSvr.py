import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class RockstarIDgetter:
    __browser__ = None

    def __init__(self):
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL'}
        self.__browser__ = webdriver.Chrome(desired_capabilities=caps)
        self.__browser__.get("https://zh-cn.socialclub.rockstargames.com")
        logs = [json.loads(log['message'])['message'] for log in self.__browser__.get_log('performance')]
        print(logs)
