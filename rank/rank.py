# coding: utf-8
__author__ = 'liufei'
import time
import random
from threading import Thread
import wx
from wx.lib.pubsub import pub
from element.page import page
from data.data import data

class rank(page, Thread):
    def __init__(self, searcher, driverType, proxyType, proxyConfig, keyworks, urlkw, runType, runtime=0):
        Thread.__init__(self)
        #搜索关键词
        self.data = data()
        self.searcher = searcher
        self.driverType = driverType
        self.gotoURL = self.getURL()
        self.proxyType = proxyType
        self.proxyConfig = proxyConfig
        self.SearchKeywords = keyworks
        self.URLKeywords = urlkw
        self.runType = runType
        self.Runtime = runtime

        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.randomArea = 5     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例
        self.baidu_keywords = ['百度', '_相关']
        # 设置线程为后台线程, 并启动线程
        self.setDaemon(True)
        self.start()

    def __del__(self):
        self.end()

    def run(self):
        self.getMethod(self.searcher, self.driverType)
        wx.CallAfter(pub.sendMessage, "reset")
        wx.CallAfter(self.output_Result, log="[All Done]")

    def getdriverType(self):
        return "h5_firefox" if self.driverType == 0 else ("h5_chrome" if self.driverType == 1 else "web_firefox")

    def getURL(self):
        return self.data.baidu_url if self.searcher == 0 else (self.data.sm_url if self.searcher == 1 else self.data.sogou_url)

    def getMethod(self, searcher, driverType):
        if [searcher, driverType] == [0, 0] or [searcher, driverType] == [0, 1]:
            self.rank_baidu_m()
        if [searcher, driverType] == [0, 2]:
            self.rank_baidu_web()
        if [searcher, driverType] == [1, 0] or [searcher, driverType] == [1, 1]:
            self.rank_sm_m()
        if [searcher, driverType] == [1, 2]:
            self.rank_sm_web()
        if [searcher, driverType] == [2, 0] or [searcher, driverType] == [2, 1]:
            self.rank_sogou_m()
        if [searcher, driverType] == [2, 2]:
            self.rank_sogou_web()

    def begin(self):
        # 实例化
        isProxy = True
        if 2 == self.runType:
            isProxy = False
        try:
            self.pageobj = page(self.getdriverType(), self.proxyType, self.proxyConfig, self.runType, isProxy)
        except Exception, e:
            self.output_Result(info=str(e))
            wx.CallAfter(pub.sendMessage, "reset")
            exit("Failed to run~!")

    def end(self):
        try:
            self.pageobj.quit()
        except:
            pass

    def rank_baidu_web(self):
        process = 1
        for kw in self.SearchKeywords.items():
            total = len(self.SearchKeywords)
            runtime = 0
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            self.output_Result(info="【%d/%d】：当前关键词 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                self.output_Result(info="当前使用代理: %s" %self.pageobj.getProxyAddr())
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.gotoURL)
                    window = driver.current_window_handle
                    self.pageobj.find_element(*self.baidu_kw).send_keys(unicode(key))
                    time.sleep(2)
                    self.pageobj.find_element(*self.baidu_submit).click()
                    time.sleep(2)
                except Exception, e:
                    self.output_Result(log=str(e))
                    self.end()
                    continue

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    self.output_Result(info="     搜索结果页面翻到第[%d]页" % (page+1))
                    pageButton = self.pageobj.find_elements(*self.baidu_result_pages)
                    if page == 0:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            self.output_Result(info="     点击结果页面第[%d]个链接" % (index+1))
                            try:
                                time.sleep(2)
                                baidu_result_items[index].click()
                            except Exception, e:
                                self.output_Result(log="     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                    else:
                        try:
                            pageButton[page].click()
                        except:
                            self.end()
                            continue
                        time.sleep(2)
                        # 等待翻页数据加载完成
                        self.pageobj.waitForPageLoad(*self.baidu_kw)

                    # 3. 遍历结果页面中的跳转URL，并点击结果URL
                    baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
                    for index in range(len(baidu_result_items)):
                        resultTitle = baidu_result_items[index].text
                        resultURL = baidu_result_items[index].get_attribute("href")
                        for kw in self.URLKeywords:
                            if kw in resultTitle:
                                self.output_Result(info="     点击结果页面第[%d]个链接: %s" % (index+1, resultURL))
                                try:
                                    time.sleep(1)
                                    baidu_result_items[index].click()
                                except Exception, e:
                                    self.output_Result(log="     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                self.end()
                runtime += 1
                wx.CallAfter(pub.sendMessage, "process", value=((((process-1)*value)+runtime)*100)/(total*value))
            process += 1
            self.output_Result(info="当前关键词，成功点击%d次" % runtime)

    def rank_baidu_m(self):
        process = 1
        for kw in self.SearchKeywords.items():
            total = len(self.SearchKeywords)
            runtime = 0
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            self.output_Result(info="【%d/%d】：当前关键词 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                self.output_Result(info="当前使用代理: %s" %self.pageobj.getProxyAddr())
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.gotoURL)
                    window = driver.current_window_handle
                    self.pageobj.find_element(*self.baidu_kw_m).send_keys(unicode(key))
                    time.sleep(2)
                    self.pageobj.find_element(*self.baidu_submit_m).click()
                    time.sleep(2)
                except Exception, e:
                    self.output_Result(log="Failed to open buidu page!")
                    self.end()
                    continue

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    found = False   # 定位到关键词排名后，跳出循环标志位
                    self.output_Result(info="     搜索结果页面翻到第[%d]页" % (page+1))
                    if page == 0:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items_m)
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            for baikw in self.baidu_keywords:
                                if baikw in baidu_result_items[index].text:
                                    isBaiduUrl = True
                                else:
                                    isBaiduUrl = False
                            self.output_Result(info="     点击结果页面第[%d]个链接" % (index+1))
                            try:
                                js = "document.querySelectorAll('%s')[%d].setAttribute('target', '_blank')"
                                driver.execute_script(js % (self.baidu_result_items_m[-1], index))
                                time.sleep(1)
                                baidu_result_items[index].click()
                                time.sleep(1)
                                # 如果目标链接是百度自己的链接，则点击后，页面运行返回操作
                                if isBaiduUrl:
                                    driver.back()
                            except Exception, e:
                                self.output_Result(log="     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                    else:
                        try:
                            self.pageobj.find_elements(*self.baidu_result_pages_m)[-1].click()
                        except:
                            self.end()
                            continue
                        time.sleep(2)
                        # 等待翻页数据加载完成
                        self.pageobj.waitForPageLoad(*self.baidu_se_kw_m)

                    # 3. 遍历结果页面中的跳转URL，并点击结果URL
                    baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items_m)
                    for index in range(len(baidu_result_items)):
                        resultTitle = baidu_result_items[index].text
                        resultURL = baidu_result_items[index].get_attribute("href")
                        for kw in self.URLKeywords:
                            if kw in resultTitle:
                                self.output_Result(info="     点击结果页面第[%d]个链接: %s" % (index+1, resultURL))
                                try:
                                    # 将结果页面中的URL修改为新页面打开
                                    js = "document.querySelectorAll('%s')[%d].setAttribute('target', '_blank')"
                                    driver.execute_script(js % (self.baidu_result_items_m[-1], index))
                                    time.sleep(2)
                                    baidu_result_items[index].click()
                                    found = True
                                    break
                                except Exception, e:
                                    self.output_Result(log="     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            if found:
                                break
                                driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                    if found:
                        break
                self.end()
                runtime += 1
                wx.CallAfter(pub.sendMessage, "process", value=((((process-1)*value)+runtime)*100)/(total*value))
            process += 1
            self.output_Result(info="当前关键词，成功点击%d次" % runtime)

    def rank_sm_web(self):
        wx.CallAfter(self.output_Result, log="该功能尚未支持!")

    def rank_sm_m(self):
        wx.CallAfter(self.output_Result, log="该功能尚未支持!")

    def rank_sogou_web(self):
        wx.CallAfter(self.output_Result, log="该功能尚未支持!")

    def rank_sogou_m(self):
        wx.CallAfter(self.output_Result, log="该功能尚未支持!")