# coding: utf-8
__author__ = 'liufei'

import sys
import os
import platform
import random
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from conf.ua import ua
reload(sys)
sys.setdefaultencoding('utf8')

class config:
    def __init__(self, driverConfig, proxy=""):
        self.remote_hub_ip = "http://192.168.99.100:4444/wd/hub"
        # self.remote_hub_ip = "http://127.0.0.1:4444/wd/hub"
        self.UA = ua()
        if driverConfig.startswith("web"):
            self.uaValue = random.choice(self.UA.USER_AGENTS_WEB)
        if driverConfig.startswith("h5"):
            self.uaValue = random.choice(self.UA.USER_AGENTS_H5)
        if proxy:
            try:
                iparray = proxy.split(":")
                ip, port = iparray[0], int(iparray[1])
            except:
                proxy, ip, port = "获取代理失败, 请检查代理配置!", "", ""
        else:
            proxy, ip, port = "获取代理失败, 请检查代理配置!", "", ""

        if driverConfig.endswith("phantomjs"):
            caps = DesiredCapabilities.PHANTOMJS
            caps["phantomjs.page.settings.resourceTimeout"] = 5000
            caps["phantomjs.page.settings.loadImages"] = False
            caps["phantomjs.page.settings.userAgent"] = self.uaValue
            service_args = [
                "--ssl-protocol=any",
                "--ignore-ssl-errors=yes",
                "--proxy=%s" % proxy,
                "--proxy-type=http",
                ]
            try:
                self.driver = webdriver.PhantomJS(
                    # executable_path="%s/drivers/" % os.environ["HOME"],
                    desired_capabilities=caps,
                    service_args=service_args,
                    )
            except Exception, e:
                assert False, "phantomjs: " + e

        elif driverConfig.endswith("firefox"):
            profile = webdriver.FirefoxProfile()
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference(
                "general.useragent.override",
                self.uaValue
            )
            profile.update_preferences()
            try:
                self.driver = webdriver.Remote(
                    # executable_path="%s/drivers/" % os.environ["HOME"],
                    command_executor=self.remote_hub_ip,
                    browser_profile=profile,
                    desired_capabilities=DesiredCapabilities.FIREFOX)
            except Exception, e:
                assert False, "firefox: " + str(e)

        elif driverConfig.endswith("chrome"):
            if platform.system() == "Darwin":
                chromedriver = "%s/drivers/" % os.environ["HOME"]
            elif platform.system() == "Windows":
                chromedriver = "C:\chromedriver\chromedriver.exe"
            os.environ["webdriver.chrome.driver"] = chromedriver
            mobile_emulation = {"deviceName": "iPhone 6 Plus"}
            option = webdriver.ChromeOptions()
            option.add_experimental_option("mobileEmulation", mobile_emulation)
            option.add_argument('--allow-running-insecure-content')
            option.add_argument('--disable-web-security')
            option.add_argument('--no-referrers')
            option.add_argument('--proxy-server=%s' % proxy)
            option.add_experimental_option("prefs", {'profile.default_content_settings.images': 2})       # disable images in chromedriver

            try:
                self.driver = webdriver.Remote(
                    # executable_path=chromedriver,
                    command_executor=self.remote_hub_ip,
                    desired_capabilities=option.to_capabilities())
            except Exception, e:
                assert False, "chrome: " + str(e)
        self.setDriver(driverConfig)

    def getDriver(self):
        return self.driver

    def setDriver(self, driverConfig):
        driver = self.getDriver()
        try: #兼容老的selenium3.3已下版本
            if driverConfig.startswith("h5"):
                driver.set_window_size(414, 900)
            driver.implicitly_wait(10)
            driver.set_script_timeout(10)
            driver.set_page_load_timeout(20)
        except:
            pass

if __name__ == "__main__":
    conf = config("web_phantomjs", "110.84.239.208:8118")
    driver = conf.getDriver()
    driver.get("https://www.baidu.com")
    print driver.page_source
    cap_dict = driver.desired_capabilities
    for key in cap_dict:
        print '%s: %s' % (key, cap_dict[key])
    print driver.current_url
    driver.quit()