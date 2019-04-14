from selenium import webdriver
from LXD.services.DBSvr import DB
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from apscheduler.schedulers.background import BackgroundScheduler
import time


class AlipaySvr:
    browser = None
    username = ""
    __db__ = None
    __scheduler__ = None

    def __init__(self):
        self.browser = webdriver.Firefox()
        # 初始化支付宝网页
        self.browser.get("https://personalweb.alipay.com/portal/i.htm")
        self.browser.implicitly_wait(500)
        self.username = self.browser.find_element_by_xpath("//a[@seed='account-zhangh-myalipay-v1']").text  # 检测登录
        print('支付宝 ' + self.username + ' 登录成功！')
        time.sleep(5)  # 别那么快
        # btnrecordmore = self.browser.find_element_by_xpath("//a[@seed='i-record-more']")
        # btnrecordmore.click()  # 转到交易记录页(新版)
        self.browser.get("https://consumeprod.alipay.com/record/advanced.htm")  # 转到交易记录页
        # 打开数据库
        self.__db__ = DB()
        # 设置定时刷新
        self.__scheduler__ = BackgroundScheduler()
        self.__scheduler__.add_job(self.mainloop_handler, 'interval', seconds=60)

    def mainloop_handler(self):
        entrance = self.browser.find_element_by_xpath("//a[@seed='global-record']")
        entrance.click()
        # self.browser.refresh()
        print('刷新一次')
        if self.browser.title == '':
            pass

    # 未完工
    def review(self):
        self.browser.get("https://consumeprod.alipay.com/record/advanced.htm")
        top_orderno = self.browser.find_element_by_xpath("//a[@id='J-tradeNo-1']").get_attribute('title')
        last_seen_orderno = self.__db__.getvar('last_seen_orderno')
        if top_orderno != last_seen_orderno:  # 有新订单
            if last_seen_orderno:
                past_toporder = self.browser.find_element_by_xpath("//a[@title=" + last_seen_orderno + "]")  # 获取上次订单位置
            else:
                past_toporder = None

            print(last_seen_orderno)
            self.__db__.setvar('last_seen_orderno', top_orderno)  # 订单检测完成
        else:
            return

    def checkoderid(self, orderid, price):
        WebDriverWait(self.browser, 20, 0.5).until(expected_conditions.title_is, '我的账单 - 支付宝')
        # gotoadvanced = self.browser.find_element_by_xpath("//a[@seed='CR-AdvancedFilter']")
        # gotoadvanced.click()
        inpkwd = self.browser.find_element_by_xpath("//input[@id='J-keyword']")
        btnsubmit = self.browser.find_element_by_xpath("//input[@id='J-set-query-form']")
        inpkwd.clear()
        inpkwd.send_keys(orderid)
        btnsubmit.click()
        self.browser.implicitly_wait(2)
        try:
            result = self.browser.find_element_by_xpath("//tr[@id='J-item-1']/td[@class='amount']/span").text
        except NoSuchElementException:
            return False
        print(result)
        amount = eval(result)
        if amount >= price:
            return amount
        else:
            return False

