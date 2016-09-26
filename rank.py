# coding: utf-8
__author__ = 'liufei'

import time, random
from page import page
from data import data
from selenium.webdriver.common.by import By

class rank(page):
    def __init__(self):
        #搜索关键词
        self.data = data()
        self.SearchKeywords = self.data.SearchKeywords.items()
        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例

    def begin(self):
        # 实例化
        self.pageobj = page()

    def end(self):
        self.pageobj.quit()

    def rank_baidu(self):
        for kw in self.SearchKeywords:
            self.total = len(self.SearchKeywords)
            self.process, self.runtime  = 1, 0
            self.key, self.value = kw[0], kw[1]
            self.output_testResult(place="【Begin】：当前关键字 - %s (%d/%d)" % (self.key, self.process, self.total))
            for click in range(self.value):
                self.begin()
                driver = self.pageobj.getDriver()
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.data.baidu)
                except:
                    continue
                window = driver.current_window_handle
                self.pageobj.find_element(*self.baidu_kw).send_keys(self.key)
                self.pageobj.find_element(*self.baidu_submit).click()
                time.sleep(2)

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    print "     搜索结果页面翻到第[%d]页" % (page+1)
                    pageButton = self.pageobj.find_elements(*self.baidu_result_pages)
                    if page == 0:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(5), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(5), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            print "         点击结果页面第[%d]个链接" % (index+1)
                            try:
                                baidu_result_items[index].click()
                                time.sleep(1)
                            except:
                                print "         8好意思，并没有点到您想要的链接.....  T_T"
                            driver.switch_to_window(window)
                    else:
                        pageButton[page].click()
                        time.sleep(2)
                        # 等待翻页数据加载完成
                        self.pageobj.waitForPageLoad(*self.baidu_kw)

                    # 3. 遍历结果页面中的跳转URL，并点击结果URL
                    baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
                    for index in range(len(baidu_result_items)):
                        resultTitle = baidu_result_items[index].text
                        resultURL = baidu_result_items[index].get_attribute("href")
                        for key in self.data.URLKeywords:
                            if key in resultTitle:
                                print "         点击结果页面第[%d]个链接: %s" % (index+1, resultURL)
                                try:
                                    baidu_result_items[index].click()
                                    time.sleep(1)
                                except:
                                    print "         8好意思，并没有点到您想要的链接.....  T_T"
                            driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                self.output_testResult(proxy=self.pageobj.getProxyAddr())
                self.end()
                self.runtime += 1
            self.process += 1
            self.output_testResult(place="【End】：当前关键字，成功点击%d次" % self.runtime)

if __name__ == "__main__":
    rank = rank()
    rank.rank_baidu()