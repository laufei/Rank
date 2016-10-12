# coding: utf-8
__author__ = 'liufei'

import os, sys, time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

reload(sys)
sys.setdefaultencoding('utf8')

class page():
    def __init__(self):
        self.baidu_m = "http://m.baidu.com/"
        self.baidu_kw_m = (By.ID, 'index-kw')  # 百度首页输入框
        self.baidu_se_kw_m = (By.ID, 'kw')  # 百度搜索结果页输入框
        self.baidu_submit_m = (By.ID, 'index-bn')  # 百度首页搜索button
        self.baidu_result_pages_m = (By.CSS_SELECTOR, 'a[class^=new-nextpage]')  # 百度搜索结果页面中翻页控件
        self.baidu_result_items_m = (By.CSS_SELECTOR, 'div[srcid^=www_]')  # 百度搜索结果页面中搜索结果模块

        chromedriver = "/Users/luca/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        mobile_emulation = {"deviceName": "Google Nexus 5"}
        option = webdriver.ChromeOptions()
        option.add_experimental_option("mobileEmulation", mobile_emulation)
        try:
            self.driver = webdriver.Chrome(
                executable_path=chromedriver,
                chrome_options=option)
        except Exception, e:
            assert False, e

        self.driver.implicitly_wait(30)
        self.driver.set_script_timeout(30)
        self.driver.set_page_load_timeout(30)

    def getDriver(self):
        return self.driver

    def quitDriver(self):
        self.getDriver().quit()

    def gotoURL(self, url):
        try:
            print "     正在打开页面：", url
            self.driver.get(url)
        except TimeoutException, e:
            print "     打开该页面超时！"
            assert False, "Timed out waiting for page load! "
        except Exception, e:
            print "     打开该页面失败！"
            assert False, "Failed to open this page! "

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

    def waitForPageLoad(self, how, what):
        try:
            WebDriverWait(self.driver, 10).until((lambda x: x.find_element(by=how, value=what)),
                                                 "Wait for element <" + what + "> time out!")
            return True
        except TimeoutException, e:
            print "     打开该页面超时！"
            assert False, "Wait for element <%s> time out!" % what

    def output_testResult(self, filename, kw='', rank=''):
        fn = filename
        with open(fn, 'a+') as ff:
            if rank:
                ff.write("      " + rank + "\n")
            if kw:
                ff.write(kw)
            ff.close()

    def scroll_page(self, pix):
        js = "document.documentElement.scrollTop+=%d" % pix
        self.driver.execute_script(js)


class getRank(page):
    def __init__(self):
        self.resultfilename = "GetRankResult.txt"
        self.PagesCount = 5  # 搜索结果页面中，遍历结果页面数量
        self.URLKeywords = [u'穷游网']
        self.SearchKeywords = [
            u'曼谷旅游',
            u'新加坡旅游',
            u'清迈旅游',
            u'大阪旅游',
            u'首尔旅游',
            u'马来西亚旅游',
            u'纽约旅游',
            u'荷兰旅游',
            u'意大利旅游',
        ]

    def begin(self):
        self.pageobj = page()
        self.driver = self.pageobj.getDriver()

    def end(self):
        self.quitDriver()

    def rank_baidu(self):
        process = 1
        self.output_testResult(self.resultfilename, kw="============开始执行时间：%s ===========\n" % time.ctime())
        for kw in self.SearchKeywords:
            found = False   # 定位到关键字排名后，跳出循环标志位
            total = len(self.SearchKeywords)
            self.output_testResult(self.resultfilename, kw="【%d/%d】当前关键字 - %s " % (process, total, kw))
            self.begin()
            # 1. 打开搜索页面并使用关键词搜索
            try:
                self.gotoURL(self.pageobj.baidu_m)
                self.find_element(*self.pageobj.baidu_kw_m).send_keys(kw)
                time.sleep(2)
                self.find_element(*self.pageobj.baidu_submit_m).click()
                time.sleep(2)
            except Exception, e:
                print e
                self.end()
                self.output_testResult(self.resultfilename, rank="排名获取失败...T_T")
                process += 1
                continue

            # 2. 翻页操作
            for page in range(self.PagesCount):
                print "     搜索结果页面翻到第[%d]页" % (page + 1)
                if page != 0:
                    try:
                        self.find_elements(*self.pageobj.baidu_result_pages_m)[-1].click()
                    except:
                        self.end()
                        self.output_testResult(self.resultfilename, rank="排名获取失败...T_T")
                        process += 1
                        continue
                    time.sleep(2)
                    # 等待翻页数据加载完成
                    self.waitForPageLoad(*self.pageobj.baidu_se_kw_m)

                baidu_result_items = self.find_elements(*self.pageobj.baidu_result_items_m)
                for index in range(len(baidu_result_items)):
                    resultTitle = baidu_result_items[index].text
                    for kw in self.URLKeywords:
                        if kw in resultTitle:
                            print "         关键字位于页面第[%d]个链接" % (index + 1)
                            self.output_testResult(self.resultfilename, rank="关键字位于第[%d]页，第[%d]个链接" % (page+1, index+1))
                            found = True
                            break
                    if found:
                        break
                    self.scroll_page(100)
                if found:
                    break
            self.end()
            process += 1

if __name__ == "__main__":
    gd = getRank()
    gd.rank_baidu()
