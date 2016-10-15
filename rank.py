# coding: utf-8
__author__ = 'liufei'

import sys, time, random, wx
from page import page
from data import data
from threading import Thread
from selenium.webdriver.common.by import By
reload(sys)
sys.setdefaultencoding('utf8')

class wxRank(wx.Panel, page):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.data = data()
        self.proxyConfig = ""
        # 选择平台：web，h5
        sampleList = ['Web', 'H5']
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rb_platform = wx.RadioBox(self, -1, "wx.RadioBox", wx.DefaultPosition, wx.DefaultSize, sampleList, 2, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_PF, self.rb_platform)
        self.rb_platform.SetLabel("Platfrom:")
        sizer.Add(self.rb_platform, 0, wx.ALL, 5)

        # 选择代理方式：dns, api，txt
        sampleList = ['DNS', 'API', 'TXT']
        self.rb_proxy = wx.RadioBox(self, -1, "wx.RadioBox", wx.DefaultPosition, wx.DefaultSize, sampleList, 3, wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_Proxy, self.rb_proxy)
        self.rb_proxy.SetLabel("Proxy Mode:")
        sizer.Add(self.rb_proxy, 0, wx.ALL, 5)

        # 代理DNS，API, TXT配置输入框
        self.proxyInfo = wx.StaticText(self, -1, label="Please input the proxy config below:")
        sizer.Add(self.proxyInfo, 0, wx.ALL, 5)
        self.proxyText = wx.TextCtrl(self, -1, value=self.data.proxy_dns, size=(400, 25))
        sizer.Add(self.proxyText, 0, wx.ALL, 5)

        # 执行log
        self.multiText = wx.TextCtrl(self, -1, value="", size=(600, 180), style=wx.TE_MULTILINE|wx.TE_READONLY) #创建一个文本控件
        sizer.Add(self.multiText, 0, wx.ALL, 5)
        self.multiText.SetInsertionPoint(0)

        # 执行按钮
        self.buttonRun = wx.Button(self, label='Run', pos=(300, 363))
        self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.buttonRun)

        # 终止按钮
        self.buttonStop = wx.Button(self, label='Stop', pos=(390, 363))
        self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.buttonStop)

        self.SetSizer(sizer)

    def EvtRadioBox_PF(self, evt):
        return self.rb_platform.GetItemLabel(self.rb_platform.GetSelection())

    def EvtRadioBox_Proxy(self, evt):
        selected = self.rb_proxy.GetItemLabel(self.rb_proxy.GetSelection())
        if selected == "DNS": self.OnClickDNS(evt)
        if selected == "API": self.OnClickAPI(evt)
        if selected == "TXT": self.OnClickTXT(evt)
        return selected

    def OnClickDNS(self, evt):
        self.proxyText.SetLabel(self.data.proxy_dns)

    def OnClickAPI(self, evt):
        self.proxyText.SetLabel(self.data.proxy_api)

    def OnClickTXT(self, evt):
        self.proxyText.SetLabel(self.data.proxy_txt)

    def OnClickRun(self, evt):
        self.proxyConfig = self.proxyText.GetValue()
        self.buttonRun.SetLabel("Running")
        evt.GetEventObject().Disable()
        from rank import rank
        drvierTyple = ""
        if self.EvtRadioBox_PF(evt) == 'Web': drvierTyple = "web_firefox"
        if self.EvtRadioBox_PF(evt) == 'H5': drvierTyple = "h5_chrome"
        rank(drvierTyple, self.EvtRadioBox_Proxy(evt), self.proxyConfig, self.printLog)

    def OnClickStop(self, evt):
        ret = wx.MessageBox('Do you really want to leave?','Confirm',wx.OK|wx.CANCEL)
        if ret == wx.OK:
            wx.GetApp().ExitMainLoop()
            evt.Skip()

    def printLog(self, log):
        self.multiText.AppendText(log)

class rank(page, Thread):
    def __init__(self, driverType, proxyType, proxyConfig, printlog):
        Thread.__init__(self)
        #搜索关键词
        self.driverType = driverType
        self.proxyType = proxyType
        self.proxyConfig = proxyConfig
        self.data = data()
        self.SearchKeywords = self.data.SearchKeywords.items()
        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.randomArea = 5     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例
        self.baidu_keywords = ['百度', '_相关']
        # 输出log方法
        self.printlog = printlog
        # 启动线程
        self.start()

    def run(self):
        if self.driverType.startswith("web"):
            self.rank_baidu_web()
        if self.driverType.startswith("h5"):
            self.rank_baidu_m()

    def begin(self):
        # 实例化
        self.pageobj = page(self.driverType, self.proxyType, self.proxyConfig)

    def end(self):
        self.pageobj.quit()

    def rank_baidu_web(self):
        process = 1
        for kw in self.SearchKeywords:
            total = len(self.SearchKeywords)
            runtime = 0
            key, value = kw[0], kw[1]
            self.output_testResult(self.printlog, place="【%d/%d】：当前关键字 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
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
                self.output_testResult(self.printlog, proxy=self.pageobj.getProxyAddr())
                self.end()
                runtime += 1
            process += 1
            self.output_testResult(self.printlog, place="当前关键字，成功点击%d次" % runtime)

    def rank_baidu_m(self):
        process = 1
        for kw in self.SearchKeywords:
            found = False   # 定位到关键字排名后，跳出循环标志位
            total = len(self.SearchKeywords)
            runtime = 0
            key, value = kw[0], kw[1]
            self.output_testResult(self.printlog, place="【%d/%d】：当前关键字 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
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
                                    found = True
                                    break
                                except Exception, e:
                                    print "         Oops，并没有点到您想要的链接.....  T_T", e
                            if found:
                                break
                                driver.switch_to_window(window)
                        self.pageobj.scroll_page(100)
                    if found:
                        break
                self.output_testResult(self.printlog, proxy=self.pageobj.getProxyAddr())
                self.end()
                runtime += 1
            process += 1
            self.output_testResult(self.printlog, place="当前关键字，成功点击%d次" % runtime)

if __name__ == "__main__":
    app = wx.App(False)
    frame = wx.Frame(None, title='刷百度排名小工具   --By Liufei', size=(500, 420), style=wx.MINIMIZE_BOX|wx.CLOSE_BOX)
    panel = wxRank(frame)
    frame.Show(True)
    app.MainLoop()