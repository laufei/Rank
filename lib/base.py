# coding: utf-8
__author__ = 'liufei'

import time
import json
import random
import wx
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from wx.lib.pubsub import pub
from conf.config import config
from conf.ua import ua
from data.data import data

class base():

    def __init__(self, platform, proxyType, proxyConfig, runType, isProxy=True, isDriver=True, rand=True):
        self.UA = ua()
        self.platform = platform
        self.ua = random.choice(self.UA.USER_AGENTS_H5) if self.platform.startswith("h5") else random.choice(self.UA.USER_AGENTS_WEB)
        self.isProxy = isProxy
        if self.isProxy:
            self.proxy = self.getProxy(proxyType, proxyConfig, rand)
            if self.proxy and "ERR" not in self.proxy:
                try:
                    self.proxy.split(":")
                except:
                    self.proxy = u"获取代理失败, 请检查代理配置!"
            else:
                self.proxy = u"获取代理失败, 请检查代理配置!"
            print u"当前使用的代理服务器：%s" % self.proxy
        else:
            self.proxy = ""

        self.runType = runType
        self.data = data()
        if isDriver:
            self.config = config(platform, self.proxy)
            self.driver = self.config.getDriver()
        self.session = requests.session()

    def __del__(self):
        try:
            self.clearCookies()
        except Exception:
            pass

    def getSession(self):
        return self.session

    def clearCookies(self):
        self.session.cookies.clear()

    def getProxyAddr(self):
        return self.proxy

    @classmethod
    def getProxy(self, type, config, rand):
        # rand False: 返回全部，True: 随机返回一个
        proxyaddr = []
        # if type == "Local":
        #     r = requests.get(config)
        #     ip_ports = json.loads(r.text)
        #     for i in ip_ports:
        #         ip = i['ip']
        #         port = i['port']
        #         proxyaddr.append(ip+":"+str(port))

        if type == "Local" or type == "API":
            reqURL = config
            try:
                response = requests.get(reqURL)
            except Exception:
                return False
            proxyaddr = response.text.split("\r\n")[:-1]
        if type == "TXT":
            filename = config
            data = list()
            try:
                with open(filename, 'r') as ff:
                    for line in ff.readlines():
                        data.append(line.split("\r\n")[0])
            except:
                return False
            proxyaddr = data
        if rand:
            return random.choice(proxyaddr)
        return proxyaddr

    def requests_url(self, url, timeout=30):
        proxy = {}
        if self.isProxy:
            proxy["http"] = "http://"+self.proxy
            # proxy["https"] = "http://"+self.proxy
            headers = {"User-Agent": self.ua,
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
                        'Connection': 'keep-alive',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                   }

        if 0 == self.runType:
            response = self.getSession().get(url, headers=headers, proxies=proxy, timeout=timeout).text
        else:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=timeout).text
        time.sleep(3)
        return response

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
            print u"     正在打开页面：", url
            self.driver.get(url)
            if self.platform.startswith("web"):
                self.driver.maximize_window()
            if self.driver.current_url.startswith("http://"):
                print u"     自动跳转到http页面, 打开该页面失败！"
                assert False, "Went to http page, failed to open https page! "
        except TimeoutException:
            print u"     打开该页面超时！"
            assert False, "Timed out waiting for page load! "
        except Exception:
            print u"     打开该页面失败！"
            assert False, "Failed to open this page! "

    def quit(self):
        try:
            self.driver.quit()
        except Exception, e:
            print u"关闭浏览器失败:", e

    def is_element_present(self, how, what):
        try:
            if self.driver.find_element(by=how, value=what).is_displayed():
                return True
        except NoSuchElementException, e:
            return False

    def isPageOpened(self, by, value):
        if not self.is_element_present(by, value):
            print u"     打开该页面失败！"
            assert False, "Unable to open this page!"

    def waitForPageLoad(self, how, what):
        try:
            WebDriverWait(self.driver, 10).until((lambda x: x.find_element(by=how, value=what)),
                                                  "Wait for element <" + what + "> time out!")
            return True
        except TimeoutException, e:
            print u"     打开该页面超时！"
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
            msg = " ["+time.strftime("%Y-%m-%d %H:%M:%S")+"]  " + log + "\n"
            wx.CallAfter(pub.sendMessage, "log", log=msg, mode=1)
        if outputfile:
            filename = "Result.txt"
            with open(filename, 'a+') as ff:
                if info:
                    msg = info+"\n"
                if log:
                    msg = " ["+time.strftime("%Y-%m-%d %H:%M:%S")+"]  " + log + "\n"
                ff.write(msg)