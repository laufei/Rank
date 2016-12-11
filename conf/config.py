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
            print "phantomjs's ua = ", self.uaValue
            caps = DesiredCapabilities.PHANTOMJS
            caps["phantomjs.page.settings.loadImages"] = False
            caps["phantomjs.page.customHeaders.User-Agent"] = self.uaValue
            service_args = [
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

        elif driverConfig == "web_firefox":
            print "web_firefox's ua = ", self.uaValue
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

        elif driverConfig == "h5_firefox":
            print "h5_firefox's ua = ", self.uaValue
            profile = webdriver.FirefoxProfile()
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference("network.proxy.share_proxy_settings", True);
            profile.set_preference("network.proxy.no_proxies_on", "localhost");
            profile.set_preference(
                "general.useragent.override",
                self.uaValue
            )
            profile.update_preferences()
            try:
                self.driver = webdriver.Firefox(
                    # executable_path= "%s/drivers/" % os.environ["HOME"],
                    firefox_profile=profile,
                    )
            except Exception, e:
                assert False, e

        elif driverConfig == "h5_chrome":
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
            option.add_experimental_option( "prefs", {'profile.default_content_settings.images': 2})       # disable images in chromedriver

            try:
                self.driver = webdriver.Chrome(
                    # executable_path=chromedriver,
                    chrome_options=option)
            except Exception, e:
                assert False, e

        # elif driverConfig == "web_remote":
        #     PROXY = proxy
        #     DesiredCapabilities.FIREFOX['proxy'] = {
        #         "httpProxy":PROXY,
        #         "ftpProxy":PROXY,
        #         "sslProxy":PROXY,
        #         "noProxy":None,
        #         "proxyType":"MANUAL",
        #         "class":"org.openqa.selenium.Proxy",
        #         "autodetect":False
        #     }
        #     try:
        #         self.driver = webdriver.Remote(
        #             "http://192.168.56.101:4444/wd/hub",
        #             DesiredCapabilities.FIREFOX)
        #     except Exception, e:
        #         assert False, e

        # elif driverConfig == "h5_remote_firefox":
        #     profile = webdriver.FirefoxProfile()
        #     profile.set_preference("network.proxy.type", 1)
        #     profile.set_preference("network.proxy.http", ip)
        #     profile.set_preference("network.proxy.http_port", port)
        #     profile.set_preference("network.proxy.share_proxy_settings", True);
        #     profile.set_preference("network.proxy.no_proxies_on", "localhost");
        #     profile.set_preference(
        #         "general.useragent.override",
        #         "Mozilla/5.0 (Linux; Android 5.1.1; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36"
        #     )
        #     profile.update_preferences()
        #     try:
        #         self.driver = webdriver.Remote(
        #             command_executor="http://192.168.56.101:4444/wd/hub",
        #             browser_profile=profile,
        #             desired_capabilities=DesiredCapabilities.FIREFOX)
        #     except Exception, e:
        #         assert False, e
        #
        # elif driverConfig == "h5_remote_chrome":
        #     mobile_emulation = {"deviceName": "Google Nexus 5"}
        #     options = webdriver.ChromeOptions()
        #     options.add_argument('--proxy-server=%s' % proxy)
        #     options.add_experimental_option("mobileEmulation", mobile_emulation)
        #     options.add_argument('--allow-running-insecure-content')
        #     options.add_argument('--disable-web-security')
        #     options.add_argument('--no-referrers')
        #     options.add_experimental_option( "prefs", {'profile.default_content_settings.images': 2})       # disable images in chromedriver
        #     try:
        #         self.driver = webdriver.Remote(
        #             command_executor="http://192.168.56.101:4444/wd/hub",
        #             desired_capabilities=options.to_capabilities())
        #     except Exception, e:
        #         assert False, e
        self.setDriver()

    def getDriver(self):
        return self.driver

    def setDriver(self):
        driver = self.getDriver()
        driver.implicitly_wait(30)
        driver.set_script_timeout(10)
        driver.set_page_load_timeout(30)

if __name__ == "__main__":
    conf = config("web_phantomjs", "110.73.9.246:8123")
    driver = conf.getDriver()
    driver.get("http://httpbin.org/headers")
    print driver.page_source
    cap_dict = driver.desired_capabilities
    for key in cap_dict:
        print '%s: %s' % (key, cap_dict[key])
    print driver.current_url
    driver.quit()