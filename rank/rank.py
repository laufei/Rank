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
    def __init__(self, searcher, driverType, isPhantomjs, proxyType, proxyConfig, keyworks, urlkw, runType, runtime=0):
        Thread.__init__(self)
        #搜索关键词
        self.data = data()
        self.searcher = searcher
        self.driverType = driverType
        self.isPhantomjs = isPhantomjs
        self.gotoURL = self.getURL()
        self.proxyType = proxyType
        self.proxyConfig = proxyConfig
        self.SearchKeywords = keyworks
        self.URLKeywords = urlkw
        self.runType = runType
        self.Runtime = runtime
        self.succTimeAll, self.succRatio = 0, 0

        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.randomArea = 5     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例
        self.baidu_keywords = [u'百度', u'_相关']
        # 设置线程为后台线程, 并启动线程
        self.setDaemon(True)
        self.start()

    def __del__(self):
        self.end()

    def run(self):
        self.getMethod(self.searcher, self.driverType)
        wx.CallAfter(pub.sendMessage, "reset")
        wx.CallAfter(self.output_Result, log="[All Done]")


    def getdriverType(self, isPhantomjs):
        if isPhantomjs:
            return "h5_phantomjs" if self.driverType == 0 else "web_phantomjs"
        else:
            return "h5_firefox" if self.driverType == 0 else "web_firefox"

    def getURL(self):
        return self.data.baidu_url if self.searcher == 0 else (self.data.sm_url if self.searcher == 1 else self.data.sogou_url)

    def getMethod(self, searcher, driverType):
        if [searcher, driverType] == [0, 0]:
            self.rank_baidu_m()
        if [searcher, driverType] == [0, 1]:
            self.rank_baidu_web()
        if [searcher, driverType] == [1, 0]:
            self.rank_sm_m()
        if [searcher, driverType] == [1, 1]:
            self.rank_sm_web()
        if [searcher, driverType] == [2, 0]:
            self.rank_sogou_m()
        if [searcher, driverType] == [2, 1]:
            self.rank_sogou_web()

    def begin(self):
        # 实例化
        isProxy = True
        if 2 == self.runType:
            isProxy = False
        try:
            self.pageobj = page(self.getdriverType(self.isPhantomjs), self.proxyType, self.proxyConfig, self.runType, isProxy)
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
        process = 0         # process: 记录已执行到第几个关键词
        self.print_kw_config(self.SearchKeywords, self.driverType, self.Runtime)
        for kw in self.SearchKeywords.items():
            process += 1
            succtime, runtime = 0, 0         # succtime: 记录当前关键字下成功点击次数;     runtime: 记录当前关键字下所有点击次数
            total = len(self.SearchKeywords)
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            self.output_Result(info=u"【%d/%d】：当前关键词 - %s" % (process, total, key))
            while True:
                if int(value) == int(succtime):
                    break
                runtime += 1
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                if 2 != self.runType:
                    self.output_Result(info=u"[%s] 当前使用代理: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), self.pageobj.getProxyAddr()))
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
                    found = False   # 定位到关键词排名后，跳出循环标志位
                    self.output_Result(info=u"     搜索结果页面翻到第[%d]页" % (page+1))
                    pageButton = self.pageobj.find_elements(*self.baidu_result_pages)
                    if page == 0 and self.runType != 2:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            self.output_Result(info=u"     点击结果页面第[%d]个链接" % (index+1))
                            try:
                                time.sleep(2)
                                baidu_result_items[index].click()
                            except Exception, e:
                                self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                        if 1 == self.runType:   # 如果选择只刷指数, 则无需翻页再进行后续操作
                            succtime += 1
                            self.succTimeAll += 1   #总的成功执行数增1
                            wx.CallAfter(pub.sendMessage, "succTime", value=self.succTimeAll)
                            print "process = ", self.succTimeAll/(total*value)
                            wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                            try:
                                self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                                wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                            except ZeroDivisionError:
                                pass
                            break
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
                                # print "穷游URL: ", resultURL
                                if self.runType == 2:       # 如果只是查询排名, 执行到这里结束
                                    self.output_Result(info=u"     关键字位于第[%d]页，第[%d]个链接" % (page+1, index+1))
                                    found = True
                                    succtime += 1
                                    break
                                self.output_Result(info=u"     点击结果页面第[%d]个链接: %s" % (index+1, resultURL))
                                try:
                                    time.sleep(1)
                                    baidu_result_items[index].click()
                                    found = True
                                    succtime += 1
                                    break
                                except Exception, e:
                                    self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                            if found:
                                break       # 点击到目标链接后, 退出点击结果页面URL循环
                        self.pageobj.scroll_page(100)
                    if found:
                        self.succTimeAll += 1   #总的成功执行数增1
                        wx.CallAfter(pub.sendMessage, "succTime", value=self.succTimeAll)
                        break                  # 点击到目标链接后, 退出翻页操作循环
                self.end()
                wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                try:
                    self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                    wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                except ZeroDivisionError:
                    pass
            if self.runType == 0:
                self.output_Result(info=u"当前关键词，成功点击%d次" % succtime)

    def rank_baidu_m(self):
        process = 0         # process: 记录已执行到第几个关键词
        self.print_kw_config(self.SearchKeywords, self.driverType, self.Runtime)
        for kw in self.SearchKeywords.items():
            process += 1
            succtime, runtime = 0, 0         # succtime: 记录当前关键字下成功点击次数;     runtime: 记录当前关键字下所有点击次数
            total = len(self.SearchKeywords)
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            self.output_Result(info=u"【%d/%d】：当前关键词 - %s" % (process, total, key))
            while True:
                if int(value) == int(succtime):
                    break
                runtime += 1
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                if 2 != self.runType:
                    self.output_Result(info=u"[%s] 当前使用代理: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), self.pageobj.getProxyAddr()))
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
                    self.output_Result(info=u"     搜索结果页面翻到第[%d]页" % (page+1))
                    if page == 0 and self.runType != 2:
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
                                try:
                                    if baikw in baidu_result_items[index].text:
                                        isBaiduUrl = True
                                    else:
                                        isBaiduUrl = False
                                except:
                                    continue
                            self.output_Result(info=u"     点击结果页面第[%d]个链接" % (index+1))
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
                                self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            driver.switch_to_window(window)
                        if 1 == self.runType:   # 如果选择只刷指数, 则无需翻页再进行后续操作
                            self.succTimeAll += 1   #总的成功执行数增1
                            succtime += 1
                            wx.CallAfter(pub.sendMessage, "succTime", value=self.succTimeAll)
                            wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                            try:
                                self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                                wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                            except ZeroDivisionError:
                                pass
                            break
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
                                # print "穷游URL: ", resultURL
                                if self.runType == 2:       # 如果只是查询排名, 执行到这里结束
                                    self.output_Result(info=u"     关键字位于第[%d]页，第[%d]个链接" % (page+1, index+1))
                                    found = True
                                    succtime += 1
                                    break
                                self.output_Result(info=u"     点击结果页面第[%d]个链接: %s" % (index+1, resultURL))
                                try:
                                    # 将结果页面中的URL修改为新页面打开
                                    js = "document.querySelectorAll('%s')[%d].setAttribute('target', '_blank')"
                                    driver.execute_script(js % (self.baidu_result_items_m[-1], index))
                                    time.sleep(2)
                                    baidu_result_items[index].click()
                                    found = True
                                    succtime += 1
                                    break
                                except Exception, e:
                                    self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                                driver.switch_to_window(window)
                            if found:
                                break       # 点击到目标链接后, 退出点击结果页面URL循环
                        self.pageobj.scroll_page(100)
                    if found:
                        self.succTimeAll += 1   #总的成功执行数增1
                        wx.CallAfter(pub.sendMessage, "succTime", value=self.succTimeAll)
                        break                  # 点击到目标链接后, 退出翻页操作循环
                self.end()
                wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                try:
                    self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                    wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                except ZeroDivisionError:
                    pass
            if self.runType == 0:
                self.output_Result(info=u"当前关键词，成功点击%d次" % succtime)

    def rank_sm_web(self):
        wx.CallAfter(self.output_Result, log=u"该功能尚未支持!")

    def rank_sm_m(self):
        wx.CallAfter(self.output_Result, log=u"该功能尚未支持!")

    def rank_sogou_web(self):
        wx.CallAfter(self.output_Result, log=u"该功能尚未支持!")

    def rank_sogou_m(self):
        wx.CallAfter(self.output_Result, log=u"该功能尚未支持!")