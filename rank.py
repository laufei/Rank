# coding: utf-8
__author__ = 'liufei'

import sys, time, random, wx
from page import page
from data import data
from selenium.webdriver.common.by import By
reload(sys)
sys.setdefaultencoding('utf8')

class BaiduRank(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # 配置代理API接口地址

        # 选择是web还是h5平台
        sampleList = ['Web', 'H5']
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rb = wx.RadioBox(self, -1, "wx.RadioBox", wx.DefaultPosition, wx.DefaultSize, sampleList, 2, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, self.rb)
        self.rb.SetLabel("Platfrom：")
        sizer.Add(self.rb, 0, wx.ALL, 15)
        self.SetSizer(sizer)

        # 执行log

        # 执行按钮
        self.button = wx.Button(self, label='Run', pos=(380, 230))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)

    def EvtRadioBox(self, evt):
        return self.rb.GetItemLabel(self.rb.GetSelection())

    def OnClick(self, evt):
        from rank import rank
        rank = rank()
        if self.EvtRadioBox(evt) == 'Web':
            rank.rank_baidu_web("web_firefox")
        if self.EvtRadioBox(evt) == 'H5':
            rank.rank_baidu_m("h5_chrome")

class rank(page):
    def __init__(self):
        #搜索关键词
        self.data = data()
        self.SearchKeywords = self.data.SearchKeywords.items()
        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.randomArea = 5     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例
        self.baidu_keywords = ['百度', '_相关']

    def begin(self, platform):
        # 实例化
        self.pageobj = page(platform)

    def end(self):
        self.pageobj.quit()

    def rank_baidu_web(self, platform):
        process = 1
        for kw in self.SearchKeywords:
            total = len(self.SearchKeywords)
            runtime = 0
            key, value = kw[0], kw[1]
            self.output_testResult(place="【WEB Begin】：当前关键字 - %s (%d/%d)" % (key, process, total))
            for click in range(value):
                self.begin(platform)
                driver = self.pageobj.getDriver()
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.pageobj.baidu)
                    window = driver.current_window_handle
                    self.pageobj.find_element(*self.baidu_kw).send_keys(key)
                    time.sleep(2)
                    self.pageobj.find_element(*self.baidu_submit).click()
                    time.sleep(2)
                except:
                    self.end()
                    continue

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
                            targets = sorted(random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                        else:
                            targets = random.sample(range(self.randomArea), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                        for index in targets:
                            print "         点击结果页面第[%d]个链接" % (index+1)
                            try:
                                time.sleep(2)
                                baidu_result_items[index].click()
                            except Exception, e:
                                print "         Oops，并没有点到您想要的链接.....  T_T", e
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
                        for kw in self.data.URLKeywords:
                            if kw in resultTitle:
                                print "         点击结果页面第[%d]个链接: %s" % (index+1, resultURL)
                                try:
                                    time.sleep(1)
                                    baidu_result_items[index].click()
                                except Exception, e:
                                    print "         Oops，并没有点到您想要的链接.....  T_T", e
                            driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                self.output_testResult(proxy=self.pageobj.getProxyAddr())
                self.end()
                runtime += 1
            process += 1
            self.output_testResult(place="【WEB End】：当前关键字，成功点击%d次" % runtime)

    def rank_baidu_m(self, platform):
        process = 1
        for kw in self.SearchKeywords:
            total = len(self.SearchKeywords)
            runtime = 0
            key, value = kw[0], kw[1]
            self.output_testResult(place="【H5 Begin】：当前关键字 - %s (%d/%d)" % (key, process, total))
            for click in range(value):
                self.begin(platform)
                driver = self.pageobj.getDriver()
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.pageobj.baidu_m)
                    window = driver.current_window_handle
                    self.pageobj.find_element(*self.baidu_kw_m).send_keys(key)
                    time.sleep(2)
                    self.pageobj.find_element(*self.baidu_submit_m).click()
                    time.sleep(2)
                except:
                    self.end()
                    continue

                # 2. 翻页操作
                for page in range(self.PagesCount):
                    print "     搜索结果页面翻到第[%d]页" % (page+1)
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
                            print "         点击结果页面第[%d]个链接" % (index+1)
                            try:
                                js = "document.querySelectorAll('%s')[%d].setAttribute('target', '_blank')"
                                driver.execute_script(js % (self.baidu_result_items_m[-1], index))
                                time.sleep(1)
                                baidu_result_items[index].click()
                                time.sleep(1)
                                # 如果目标链接是百度自己的链接，则点击后，页面执行返回操作
                                if isBaiduUrl:
                                    driver.back()
                            except Exception, e:
                                print "         Oops，并没有点到您想要的链接.....  T_T", e
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
                        for kw in self.data.URLKeywords:
                            if kw in resultTitle:
                                print "         点击结果页面第[%d]个链接: %s" % (index+1, resultURL)
                                try:
                                    # 将结果页面中的URL修改为新页面打开
                                    js = "document.querySelectorAll('%s')[%d].setAttribute('target', '_blank')"
                                    driver.execute_script(js % (self.baidu_result_items_m[-1], index))
                                    time.sleep(2)
                                    baidu_result_items[index].click()
                                except Exception, e:
                                    print "         Oops，并没有点到您想要的链接.....  T_T", e
                                driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                self.output_testResult(proxy=self.pageobj.getProxyAddr())
                self.end()
                runtime += 1
            process += 1
            self.output_testResult(place="【H5 End】：当前关键字，成功点击%d次" % runtime)

if __name__ == "__main__":
    app = wx.App(False)
    frame = wx.Frame(None, title='百度刷排名小工具   --By Liufei', size=(500, 300), style=wx.MINIMIZE_BOX|wx.CLOSE_BOX)
    panel = BaiduRank(frame)
    frame.Show()
    app.MainLoop()