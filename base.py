# coding: utf-8
__author__ = 'liufei'

import wx
import time
import requests
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from config import config
from data import data
from wx.lib.pubsub import pub

class base():

    def __init__(self, platform, proxyType, proxyConfig, isDriver=True, rand=True):
        USER_AGENTS = [
                "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4",
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2725.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/52.0.2725.0 Mobile/13B143 Safari/601.1.46",
                "Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/52.0.2725.0 Mobile/13B143 Safari/601.1.46",
                "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166",
                "Mozilla/5.0 (Android 4.4; Mobile; rv:46.0) Gecko/46.0 Firefox/46.0",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1",
        ]
        self.ua = USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]
        self.proxy = self.getProxy(proxyType, proxyConfig, rand)
        if self.proxy and not "ERR" in self.proxy:
            try:
                self.proxy.split(":")
            except:
                self.proxy = "获取代理失败, 请检查代理配置!"
        else:
            self.proxy = "获取代理失败, 请检查代理配置!"

        print "当前使用的代理服务器：%s" % self.proxy
        self.data = data()
        if isDriver:
            self.config = config(platform, self.proxy)
            self.driver = self.config.driver

    def getProxyAddr(self):
        return self.proxy

    def getProxy(self, type, config, rand):
        # type 0: api接口获取，1: 文件获取
        # rand False: 返回全部，True: 随机返回一个
        proxyaddr = ""
        if type == "DNS":
            proxyaddr = config
            return proxyaddr
        if type == "API":
            reqURL = config
            try:
                response = requests.get(reqURL)
            except Exception, e:
                return False
            proxyaddr = response.text.split("\r\n")
        if type == "TXT":
            filename = config
            try:
                with open(filename, 'r') as ff:
                    data = ff.readlines()
            except:
                return False
            proxyaddr = data[0].split("\r")
        if rand:
            return proxyaddr[random.randint(0, len(proxyaddr)-1)]
        return proxyaddr

    def requests_url(self, platform, url):
        headers = ""
        proxy = {}
        proxy["http"] = "http://"+self.proxy
        if platform == "M":
            headers = {"User-Agent": self.ua}
        return requests.get(url, headers=headers, proxies=proxy, timeout=30).text

    def getDriver(self):
        return self.driver

    def find_element(self, by, view):
        try:
            return self.driver.find_element(by, view)
        except TimeoutException, e:
            assert False, e

    def find_elements(self, by, view):
        try:
            return self.driver.find_elements(by, view)
        except TimeoutException, e:
            assert False, e

    def gotoURL(self, url):
        try:
            print "     正在打开页面：", url
            self.driver.get(url)
            if not self.driver.capabilities["platform"] in ["android", "ANDROID", "Android"]:
                self.driver.maximize_window()
        except TimeoutException, e:
            print "     打开该页面超时！"
            assert False, "Timed out waiting for page load! "
        except Exception, e:
            print "     打开该页面失败！"
            assert False, "Failed to open this page! "

    def quit(self):
        try:
            self.driver.quit()
        except Exception, e:
            print e

    def is_element_present(self, how, what):
        try:
            if self.driver.find_element(by=how, value=what).is_displayed():
                return True
        except NoSuchElementException, e:
            return False

    def isPageOpened(self, by, value):
        if not self.is_element_present(by, value):
            print "     打开该页面失败！"
            assert False, "Unable to open this page!"

    def waitForPageLoad(self, how, what):
        try:
            WebDriverWait(self.driver, 10).until((lambda x: x.find_element(by=how, value=what)),
                                                  "Wait for element <" + what + "> time out!")
            return True
        except TimeoutException, e:
            print "     打开该页面超时！"
            assert False, "Wait for element <%s> time out!" % what

    def goto_other_window(self):
        winBeforeHandle = self.driver.current_window_handle
        winHandles = self.driver.window_handles
        for handle in winHandles:
            if winBeforeHandle != handle:
                self.driver.switch_to.window(handle)
                time.sleep(3)
                self.driver.execute_script("window.stop()")

    def close_other_windows(self):
        winBeforeHandle = self.driver.current_window_handle
        winHandles = self.driver.window_handles

        for handle in winHandles:
            if winBeforeHandle != handle:
                self.driver.switch_to.window(handle)
                time.sleep(2)
                self.driver.execute_script("window.stop()")
                self.driver.close()

    def scroll_page(self, pix):
        js = "document.documentElement.scrollTop+=%d" % pix
        self.driver.execute_script(js)

    def output_Result(self, log='', info='', outputfile=True):
        msg = ""
        if info:
            msg = info+"\n"
            wx.CallAfter(pub.sendMessage, "info", info=msg)
        if log:
            msg = " ["+time.ctime()+"]  " + log + "\n"
            wx.CallAfter(pub.sendMessage, "log", log=msg, mode=1)
        if outputfile:
            filename = "Result.txt"
            with open(filename, 'a+') as ff:
                if info:
                    msg = info+"\n"
                if log:
                    msg = " ["+time.ctime()+"]  " + log + "\n"
                ff.write(msg)