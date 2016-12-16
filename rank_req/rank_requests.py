# coding: utf-8
__author__ = 'liufei'
import random, time
from threading import Thread
import wx
from BeautifulSoup import BeautifulSoup as BS
from wx.lib.pubsub import pub
from lib.base import base
from data.data import data


class rank_requests(base, Thread):
    def __init__(self, searcher, platform, proxyType, proxyConfig, keyworks, urlkw, runType, runtime=0):
        Thread.__init__(self)
        self.data = data()
        self.searcher = searcher
        self.platform = platform
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
        if self.runType==1:
            self.randomArea = 3     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例

        # 设置线程为后台线程, 并启动线程
        self.setDaemon(True)
        self.start()

    def run(self):
        self.getMethod(self.searcher, self.platform)
        wx.CallAfter(pub.sendMessage, "reset")
        wx.CallAfter(self.output_Result, log=u"[All Done] 运行结果请查看日志文件: Result.txt")

    def getPlatform(self):
        return "h5" if self.platform == 0 else "web"

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
            self.baseobj = base(self.getPlatform(), self.proxyType, self.proxyConfig, self.runType, isProxy, False)
        except Exception, e:
            self.output_Result(info=str(e))
            wx.CallAfter(pub.sendMessage, "reset")
            exit("Failed to run~!")

    def end(self):
        pass

    def rank_baidu_web(self):
        process = 0         # process: 记录已执行到第几个关键词
        self.print_kw_config(self.SearchKeywords, self.platform, self.Runtime)
        for kw in self.SearchKeywords.items():
            process += 1
            succtime, runtime = 0, 0         # succtime: 记录当前关键字下成功请求次数;     runtime: 记录当前关键字下所有请求次数
            total = len(self.SearchKeywords)
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            self.output_Result(info=u"【%d/%d】：当前关键词 - %s" % (process, total, key))
            while True:
                if int(value) == int(succtime):
                    break
                runtime += 1
                self.begin()
                self.output_Result(info="----------------------------------------------")
                if 2 != self.runType:
                    self.output_Result(info=u"[%s] 当前使用代理: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), self.pageobj.getProxyAddr()))
                # 1. 打开搜索页面并使用关键词搜索
                baiduPage = self.baseobj.requests_url(self.data.baidu_url_request_web % (key, 0))

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    found = False   # 定位到关键词排名后，跳出循环标志位
                    self.output_Result(info=u"     搜索结果页面翻到第[%d]页" % (page+1))
                    if page == 0 and self.runType != 2:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        soup = BS(baiduPage)
                        if self.runType == 0:
                            searchResult = soup.findAll(name="h3", attrs={"class": "t"}, limit=self.randomArea)
                        elif self.runType == 1:
                            searchResult = soup.findAll(name="h3", attrs={"class": "t"})
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            self.output_Result(info=u"     点击结果页面第[%d]个链接" % (index+1))
                            try:
                                resultURL = BS(str(searchResult[index])).findAll("a")[0]["href"]
                                self.baseobj.requests_url(resultURL)
                            except Exception, e:
                                self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                        if 1 == self.runType:
                            self.succTimeAll += 1   #总的成功执行数增1
                            wx.CallAfter(pub.sendMessage, "succTime", value=(self.succTimeAll))
                            wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                            try:
                                self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                                wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                            except ZeroDivisionError:
                                pass
                            break
                    else:
                        if page > 0:
                            try:
                                baiduPage = self.baseobj.requests_url(self.data.baidu_url_request_web % (key, page*10))
                            except Exception, e:
                                self.output_Result(log=u"     Oops，翻页失败...... T_T, %s" % str(e))
                                self.end()
                                continue

                    # 3. 遍历结果页面中的跳转URL，并点击结果URL
                    soup = BS(baiduPage)
                    searchResult = soup.findAll(name="h3", attrs={"class": "t"})
                    for index in range(len(searchResult)):
                        try:
                            resultTitle = BS(str(searchResult[index])).findAll("a")[0].getText()
                            resultURL = BS(str(searchResult[index])).findAll("a")[0]["href"]
                        except Exception:
                            continue
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
                                    self.baseobj.requests_url(resultURL)
                                    found = True
                                    succtime += 1
                                    break
                                except Exception, e:
                                    self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            if found:
                                break
                    if found:
                        self.succTimeAll += 1   #总的成功执行数增1
                        wx.CallAfter(pub.sendMessage, "succTime", value=(self.succTimeAll))
                        break
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
        self.print_kw_config(self.SearchKeywords, self.platform, self.Runtime)
        for kw in self.SearchKeywords.items():
            process += 1
            succtime, runtime = 0, 0         # succtime: 记录当前关键字下成功请求次数;     runtime: 记录当前关键字下所有请求次数
            total = len(self.SearchKeywords)
            key = kw[0]
            value = (kw[1] if not self.Runtime else self.Runtime)
            while True:
                self.output_Result(info=u"【%d/%d】：当前关键词 - %s" % (process, total, key))
                if int(value) == int(succtime):
                    break
                runtime += 1
                self.begin()
                self.output_Result(info="----------------------------------------------")
                if 2 != self.runType:
                    self.output_Result(info=u"[%s] 当前使用代理: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), self.pageobj.getProxyAddr()))
                # 1. 打开搜索页面并使用关键词搜索
                baiduPage = self.baseobj.requests_url(self.data.baidu_url_request_m % (key, 0))

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    found = False   # 定位到关键词排名后，跳出循环标志位
                    self.output_Result(info=u"     搜索结果页面翻到第[%d]页" % (page+1))
                    if page == 0 and self.runType != 2:
                        # 如果是第一页的话，随机从前五中随机点击若干(1-self.randomNo_firstpage)个URL
                        soup = BS(baiduPage)
                        searchResult = soup.findAll(name="div", attrs={"class": "c-container"}, limit=self.randomArea)
                        # 按照比例随机点击URL，正序80%，乱序20%
                        ra = random.random()
                        if ra < self.radio_sorted:
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            self.output_Result(info=u"     点击结果页面第[%d]个链接" % (index+1))
                            try:
                                resultURL = BS(str(searchResult[index])).findAll("a")[0]["href"]
                                self.baseobj.requests_url(resultURL)
                            except Exception, e:
                                self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                        if 1 == self.runType:
                            self.succTimeAll += 1   #总的成功执行数增1
                            wx.CallAfter(pub.sendMessage, "succTime", value=(self.succTimeAll))
                            wx.CallAfter(pub.sendMessage, "process", value=self.succTimeAll*100/(total*value))
                            try:
                                self.succRatio = '%.2f' % (self.succTimeAll/float((process-1)*value+runtime))
                                wx.CallAfter(pub.sendMessage, "succRatio", value=(self.succRatio))
                            except ZeroDivisionError:
                                pass
                            break
                    else:
                        if page > 0:
                            try:
                                baiduPage = self.baseobj.requests_url(self.data.baidu_url_request_m % (key, page*10))
                            except Exception, e:
                                self.output_Result(log=u"     Oops，翻页失败...... T_T, %s" % str(e))
                                self.end()
                                continue

                    # 3. 遍历结果页面中的跳转URL，并点击结果URL
                    soup = BS(baiduPage)
                    searchResult = soup.findAll(name="div", attrs={"class": "c-container"})
                    for index in range(len(searchResult)):
                        try:
                            resultTitle = BS(str(searchResult[index])).findAll("h3")[0].getText()
                            resultURL = BS(str(searchResult[index])).findAll("a")[0]["href"]
                        except Exception:
                            continue
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
                                    self.baseobj.requests_url(resultURL)
                                    found = True
                                    succtime += 1
                                    break
                                except Exception, e:
                                    self.output_Result(log=u"     Oops，并没有点到您想要的链接.....  T_T, %s" % str(e))
                            if found:
                                break
                    if found:
                        self.succTimeAll += 1   #总的成功执行数增1
                        wx.CallAfter(pub.sendMessage, "succTime", value=(self.succTimeAll))
                        break
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