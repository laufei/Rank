# coding: utf-8
__author__ = 'liufei'

import os
import time
import random
import wx
from page import page
from data import data
from threading import Thread

class wxRank(wx.Panel, page):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.data = data()
        self.keyworks = ""
        self.proxyConfig = ""
        self.initWindow()

    def initWindow(self):
            vbox = wx.BoxSizer(wx.HORIZONTAL)
            leftbox = wx.BoxSizer(wx.VERTICAL)
            fm = wx.StaticBox(self, -1, "Keywords File:")
            filebox = wx.StaticBoxSizer(fm, wx.HORIZONTAL)
            # 选择keywords文件
            self.kwText = wx.TextCtrl(self, -1, size=(200, 21))
            self.kwBtn = wx.Button(self, label='...', size=(30, 21))
            self.Bind(wx.EVT_BUTTON, self.OnOpenFile, self.kwBtn)
            # 选择平台：web，h5
            sampleList = ['Web', 'H5']
            self.rb_platform = wx.RadioBox(self, -1, "Platform:", wx.DefaultPosition, wx.DefaultSize, sampleList, 2)
            self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_PF, self.rb_platform)
            pm= wx.StaticBox(self, -1, "Proxy Mode:")
            proxyBox = wx.StaticBoxSizer(pm, wx.VERTICAL)
            # 选择代理方式：dns, api，txt
            sampleList = ['DNS', 'API', 'TXT']
            self.rb_proxy = wx.RadioBox(self, 0, "", wx.DefaultPosition, wx.DefaultSize, sampleList, 3)
            self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_Proxy, self.rb_proxy)
            # 代理DNS，API, TXT配置输入框
            self.proxyText = wx.TextCtrl(self, -1, value=self.data.proxy_dns, size=(220, 21))
            proxyBox.Add(self.rb_proxy, 0, wx.ALL|wx.ALL, 5)
            proxyBox.Add(self.proxyText, 0, wx.ALL|wx.ALL, 5)

            # 左侧布局
            filebox.Add(self.kwText, 0, wx.ALIGN_LEFT, 5)
            filebox.Add(self.kwBtn, 0, wx.ALIGN_RIGHT, 5)
            leftbox.Add(filebox, 0, wx.ALL, 5)
            leftbox.Add(self.rb_platform, 0, wx.ALL, 5)
            leftbox.Add(proxyBox, 0, wx.ALL, 5)

            # 执行log
            rightBox = wx.BoxSizer(wx.VERTICAL)
            om = wx.StaticBox(self, 0, "Log:")
            logBox = wx.StaticBoxSizer(om, wx.HORIZONTAL)
            self.multiText = wx.TextCtrl(self, 0, value="", size=(480, 160), style=wx.TE_MULTILINE|wx.TE_READONLY) #创建一个文本控件
            self.multiText.SetInsertionPoint(0)
            # 执行按钮
            btnBox = wx.BoxSizer(wx.HORIZONTAL)
            self.buttonRun = wx.Button(self, label="Run")
            self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.buttonRun)
            # 终止按钮
            self.buttonStop = wx.Button(self, label="Close")
            self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.buttonStop)

            # 右侧布局
            logBox.Add(self.multiText, 0, wx.ALL, 5)
            btnBox.Add(self.buttonRun, 0, wx.ALL, 5)
            btnBox.Add(self.buttonStop, 0, wx.ALL, 5)
            rightBox.Add(logBox, 0, wx.ALL, 5)
            rightBox.Add(btnBox, 0, wx.ALIGN_RIGHT, 5)

            # 整体布局
            vbox.Add(leftbox, 0, wx.ALL|wx.ALL, 5)
            vbox.Add(rightBox, 0, wx.ALL|wx.ALL, 5)
            self.SetSizer(vbox)

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
        # 如果未选择keyworks文件, 提示错误
        if self.keyworks == "":
            self.multiText.SetBackgroundColour("#FFC1C1")
            self.multiText.SetValue("Failed to read keywords, please check the keywords file!")
            return
        self.proxyConfig = self.proxyText.GetValue().strip()
        if self.proxyConfig == "":
            self.multiText.SetBackgroundColour("#FFC1C1")
            self.multiText.SetValue("Please input proxy config in <Proxy Mode:>!")
            return
        self.multiText.SetValue("")
        self.buttonRun.SetLabel("Running")
        self.buttonStop.SetLabel("Stop")
        evt.GetEventObject().Disable()
        from rank import rank
        drvierTyple = ""
        if self.EvtRadioBox_PF(evt) == 'Web': drvierTyple = "web_firefox"
        if self.EvtRadioBox_PF(evt) == 'H5': drvierTyple = "h5_chrome"
        rank(drvierTyple, self.EvtRadioBox_Proxy(evt), self.proxyConfig, self.printLog, self.keyworks)

    def OnClickStop(self, evt):
        ret = wx.MessageBox('Do you really want to close?', 'Confirm', wx.OK|wx.CANCEL)
        if ret == wx.OK:
            wx.Exit()

    def OnOpenFile(self, evt):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "Open file...", os.getcwd(), style=wx.FC_OPEN, wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            kwfilename = dlg.GetPath()
            self.kwText.SetLabel(kwfilename)
            self.multiText.SetValue("")
            self.keyworks = self.kyFileHeadle(kwfilename)
        dlg.Destroy()

    def kyFileHeadle(self, filename):
        try:
            with open(filename, "r") as ff:
                kw = ff.read()
                return eval(kw)
        except Exception, e:
            self.multiText.SetBackgroundColour("#FFC1C1")
            self.multiText.SetValue("Failed to get keywords:\n%s" % str(e))
            return ""

    def printLog(self, log):
        try:
            self.multiText.AppendText(log)
        except Exception, e:
            self.multiText.AppendText(str(e))

class rank(page, Thread):
    def __init__(self, driverType, proxyType, proxyConfig, printlog, keyworks):
        Thread.__init__(self)
        #搜索关键词
        self.driverType = driverType
        self.proxyType = proxyType
        self.proxyConfig = proxyConfig
        self.data = data()
        self.SearchKeywords = keyworks
        # 常量设置
        self.PagesCount = 3     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.randomArea = 5     # 首页随机点击URL范围
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例
        self.baidu_keywords = ['百度', '_相关']
        # 输出log方法
        self.printlog = printlog
        # 设置线程为后台线程, 并启动线程
        self.setDaemon(True)
        self.start()

    def __del__(self):
        self.end()

    def run(self):
        if self.driverType.startswith("web"):
            self.rank_baidu_web()
        if self.driverType.startswith("h5"):
            self.rank_baidu_m()

    def begin(self):
        # 实例化
        self.pageobj = page(self.driverType, self.proxyType, self.proxyConfig)

    def end(self):
        try:
            self.pageobj.quit()
        except:
            pass

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
    frame = wx.Frame(None, title='刷百度排名小工具 [By LiuFei]', size=(700, 280), style=wx.MINIMIZE_BOX|wx.CLOSE_BOX)
    panel = wxRank(frame)
    frame.Show(True)
    app.MainLoop()