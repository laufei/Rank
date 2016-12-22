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
                assert False, e

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
                self.driver = webdriver.Firefox(
                    # executable_path="%s/drivers/" % os.environ["HOME"],
                    firefox_profile=profile,
                    )
            except Exception, e:
                assert False, e

        elif driverConfig.endswith("chrome"):
            if platform.system() == "Darwin":
                chromedriver = "%s/drivers/" % os.environ["HOME"]
            elif platform.system() == "Windows":
                chromedriver = "C:\chromedriver\chromedriver.exe"
            os.environ["webdriver.chrome.driver"] = chromedriver
            mobile_emulation = {"deviceName": "Google Nexus 5"}
            option = webdriver.ChromeOptions()
            option.add_experimental_option("mobileEmulation", mobile_emulation)
            option.add_argument('--allow-running-insecure-content')
            option.add_argument('--disable-web-security')
            option.add_argument('--no-referrers')
            option.add_argument('--proxy-server=%s' % proxy)
            option.add_experimental_option("prefs", {'profile.default_content_settings.images': 2})       # disable images in chromedriver

            try:
                self.driver = webdriver.Chrome(
                    # executable_path=chromedriver,
                    chrome_options=option)
            except Exception, e:
                assert False, e
        self.setDriver(driverConfig)

    def getDriver(self):
        return self.driver

    def setDriver(self, driverConfig):
        driver = self.getDriver()
        if driverConfig.startswith("h5"):
            driver.set_window_size(414, 900)
        driver.implicitly_wait(10)
        driver.set_script_timeout(10)
        driver.set_page_load_timeout(10)

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