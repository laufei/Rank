# coding: utf-8
__author__ = 'liufei'

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import time

class config:
    def __init__(self, driverConfig=1, proxy=""):
        # 1 - 本地浏览器配置代理；2 - windows测试机配置代理；
        iparray = proxy.split(":")
        if len(iparray) == 2:
            ip, port = iparray[0], int(iparray[1])
        else:
            ip, port = "", ""
        print "当前使用的代理服务器：%s" % proxy
        if driverConfig == 1:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", port)
            profile.update_preferences()
            try:
                self.driver = webdriver.Firefox(firefox_profile=profile)
            except Exception, e:
                assert False, e
        elif driverConfig == 2:
            PROXY = proxy
            webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
                "httpProxy":PROXY,
                "ftpProxy":PROXY,
                "sslProxy":PROXY,
                "noProxy":None,
                "proxyType":"MANUAL",
                "class":"org.openqa.selenium.Proxy",
                "autodetect":False
            }
            try:
                self.driver = webdriver.Remote(
                    'http://192.168.56.101:4444/wd/hub',
                    webdriver.DesiredCapabilities.FIREFOX)
            except Exception, e:
                assert False, e

    def output_testResult(self, filename, result):
        with open(filename, 'a+') as ff:
            ff.write("["+time.ctime()+"]"+"         ")
            ff.write(result)
            ff.close()

        self.driver.implicitly_wait(30)
        self.driver.set_script_timeout(30)
        self.driver.set_page_load_timeout(100)