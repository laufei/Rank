# coding: utf-8
__author__ = 'liufei'

import time
import random
import json
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
        self.ua = self.UA.USER_AGENTS_H5[random.randint(0, len(self.UA.USER_AGENTS_H5)-1)] if platform == "M" else self.UA.USER_AGENTS_WEB[random.randint(0, len(self.UA.USER_AGENTS_WEB)-1)]
        self.isProxy = isProxy
        if self.isProxy:
            self.proxy = self.getProxy(proxyType, proxyConfig, rand)
            if self.proxy and not "ERR" in self.proxy:
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
            self.driver = self.config.driver
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
        if type == "Local":
            r = requests.get(config)
            ip_ports = json.loads(r.text)
            for i in ip_ports:
                ip = i['ip']
                port = i['port']
                proxyaddr.append(ip+":"+str(port))
        if type == "API":
            reqURL = config
            try:
                response = requests.get(reqURL)
            except Exception:
                return False
            proxyaddr = response.text.split("\r\n")
        if type == "TXT":
            filename = config
            data = list()
            try:
                with open(filename, 'r') as ff:
                    for line in ff.readlines():
                        data.append(line[:-2])
            except:
                return False
            proxyaddr = data
        if rand:
            return random.choice(proxyaddr)
        return proxyaddr

    def requests_url(self, url, timeout=10):
        proxy = {}
        if self.isProxy:
            proxy["http"] = "http://"+self.proxy
        headers = {"User-Agent": self.ua}
        if 0 == self.runType:
            response = self.getSession().get(url, headers=headers, proxies=proxy, timeout=timeout, verify=True).text
        else:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=timeout, verify=True).text
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
            self.driver.maximize_window()
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