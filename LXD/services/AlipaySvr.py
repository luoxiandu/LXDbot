import nonebot
from selenium import webdriver
from LXD.services.DBSvr import DB
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
import re
import random


class AlipaySvr:
    browser = None
    username = ""
    __db__ = None
    __scheduler__ = None
    __FirefoxProfile__ = "data/FirefoxProfile"
    __QQbot__ = nonebot.get_bot()
    __mainloop_job__ = None

    def __init__(self):
        self.browser = webdriver.Firefox(firefox_profile=self.__FirefoxProfile__)
        # 初始化支付宝网页
        self.browser.get("https://personalweb.alipay.com/portal/i.htm")
        self.browser.implicitly_wait(500)
        self.username = self.browser.find_element_by_xpath("//a[@seed='account-zhangh-myalipay-v1']").text  # 检测登录
        print('支付宝 ' + self.username + ' 登录成功！')
        time.sleep(5)  # 别那么快
        entrance = self.browser.find_element_by_xpath("//a[@seed='global-record']")  # 模拟点击跳转记录页
        entrance.click()
        # self.browser.get("https://consumeprod.alipay.com/record/advanced.htm")  # 转到交易记录页
        # 打开数据库
        self.__db__ = DB()
        # 设置定时刷新
        self.__scheduler__ = AsyncIOScheduler()
        self.__mainloop_job__ = self.__scheduler__.add_job(self.mainloop_handler, 'interval', seconds=60)
        self.__scheduler__.start()

    async def mainloop_handler(self):
        time.sleep(random.random())
        # 刷新页面
        entrance = self.browser.find_element_by_xpath("//a[@seed='global-record']")
        entrance.click()
        # self.browser.refresh()
        self.browser.implicitly_wait(5)
        # 判断页面是否正常
        if self.browser.title == '登录 - 支付宝':
            self.__mainloop_job__.pause()
            scrshot = self.browser.get_screenshot_as_base64()
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + scrshot
                }
            }
            for uid in [91637225, 1158395892]:
                await self.__QQbot__.send_private_msg(user_id=uid, message='登录失效，请尽快修复！')
                # await self.__QQbot__.send_private_msg(user_id=uid, message=msg)
            self.__mainloop_job__.resume()
            pass
        if self.browser.title == '安全校验 - 支付宝':
            self.__mainloop_job__.pause()
            scrshot = self.browser.get_screenshot_as_base64()
            msg = {
                'type': 'image',
                'data': {
                    'file': 'base64://' + scrshot
                }
            }
            for uid in [916327225, 1158395892]:
                await self.__QQbot__.send_private_msg(user_id=uid, message='需要安全校验，请尽快修复！')
                # await self.__QQbot__.send_private_msg(user_id=uid, message=msg)
            self.__mainloop_job__.resume()
            pass
        # 进行review
        self.review()

    # 监测订单信息
    def review(self):
        top_tradeNostr = self.browser.find_element_by_xpath("//tr[@id='J-item-1']/td[contains(@class,'tradeNo')]/p").text
        # top_orderno = self.browser.find_element_by_xpath("//a[@id='J-tradeNo-1']").get_attribute('title')
        last_seen_tradeNostr = self.__db__.getvar('Alipay_last_seen_orderno')
        if top_tradeNostr != last_seen_tradeNostr:  # 有新订单
            for item in self.browser.find_elements_by_xpath("//table[@id='tradeRecordsIndex']/tbody/tr"):
                memo = item.find_element_by_xpath("./p[@class='memo-info']").text
                tradeNostr = item.find_element_by_xpath("./td[contains(@class,'tradeNo')]/p").text
                if last_seen_tradeNostr:
                    if tradeNostr == last_seen_tradeNostr:
                        break
                restr = r"流水号:\d+"
                tradeNO = re.search(restr, tradeNostr)
                if tradeNO:
                    tradeNO = tradeNO.group().strip('流水号:')
                else:
                    continue
                amount = repr(item.find_element_by_xpath("./td[@class='amount']/span").text)  # 字符串转换
                amount = int(amount * 100)  # 单位换算
                print(tradeNO)
                print(memo)
                print(amount)
                self.__db__.saveAlipayTradeNo({
                    'tradeNo': tradeNO,
                    'memo': memo,
                    'amount': amount
                })
            print(last_seen_tradeNostr)
            self.__db__.setvar('Alipay_last_seen_orderno', top_tradeNostr)  # 订单检测完成
            return
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

