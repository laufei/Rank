# coding: utf-8
__author__ = 'liufei'

import sys, time, requests, random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from config import config
reload(sys)
sys.setdefaultencoding('utf8')

class base():

    def __init__(self, platform, proxyType, rand=True):
        self.proxy = self.getProxy(type=proxyType, rand=rand)
        self.config = config(platform, self.proxy)
        self.driver = self.config.driver

    def getProxyAddr(self):
        return self.proxy

    def getProxy(self, type, rand):
        # type 0: api接口获取，1: 文件获取
        # rand False: 返回全部，True: 随机返回一个
        proxyaddr = ""
        if type == "API":
            reqURL = "http://dev.kuaidaili.com/api/getproxy/?orderid=967269662653487&num=999&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_ha=1&sp1=1&sp2=1&sep=1"
            try:
                response = requests.get(reqURL)
            except Exception, e:
                assert False, e
            proxyaddr = response.text.split("\r\n")
        if type == "TXT":
            filename = "proxy.txt"
            with open(filename, 'r') as ff:
                data = ff.readlines()
            proxyaddr = data[0].split("\r")
        if rand:
            return proxyaddr[random.randint(0, len(proxyaddr)-1)]
        return proxyaddr

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

    def output_testResult(self, proxy='', place=''):
        filename = "TestResult.txt"
        msg = ""
        with open(filename, 'a+') as ff:
            if place:
                msg = place+"\n"
            if proxy:
                msg = "              ["+time.ctime()+"]"+"         " + proxy + "\n"
            ff.write(msg)