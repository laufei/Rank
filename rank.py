# coding: utf-8
__author__ = 'liufei'

import os, time, random, wx
from page import page
from data import data
from threading import Thread
from wx.lib.pubsub import pub

class wxRank(wx.Panel, page):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.data = data()
        self.keyworks = ""
        self.proxyType = ""
        self.proxyConfig = ""
        self.dir = "/Users/%s/drivers/" % os.environ["USER"]
        self.initWindow()
        self.update()

    def initWindow(self):
        # 选择keywords文件
        fm = wx.StaticBox(self, -1, "指定搜索关键词文件路径:")
        self.kwText = wx.TextCtrl(self, -1, value="点击右侧按钮选择文件...", size=(198, 21))
        self.kwText.SetEditable(False)
        self.kwBtn = wx.Button(self, label='...', size=(30, 21))
        self.Bind(wx.EVT_BUTTON, self.OnOpenKWFile, self.kwBtn)
        self.tmpBtn = wx.Button(self, label='+', size=(30, 21))
        self.Bind(wx.EVT_BUTTON, self.OnCreateTmpFile, self.tmpBtn)
        # 关键词运行次数
        rm = wx.StaticBox(self, -1, "运行次数:")
        self.runTime = wx.CheckBox(self, -1, "是否统一配置?  运行次数:")
        self.runText = wx.TextCtrl(self, -1, size=(65, 21))
        self.runText.SetEditable(False)
        self.runText.SetValue("10")
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox_RT, self.runTime)
        # 选择平台：web，h5
        dm = wx.StaticBox(self, -1, "运行平台:")
        sampleList = ["H5-F", "H5-C", "Web-F"]
        self.rb_platform = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, sampleList, 3)
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_PF, self.rb_platform)
        self.dndBtn = wx.Button(self, label='+', size=(30, 30))
        self.Bind(wx.EVT_BUTTON, self.cpDriver, self.dndBtn)
        # 选择代理方式：dns, api，txt
        pm = wx.StaticBox(self, -1, "代理方式:")
        sampleList = ["API", "DNS", "TXT"]
        self.rb_proxy = wx.RadioBox(self, 0, "", wx.DefaultPosition, wx.DefaultSize, sampleList, 3)
        self.proxyType = self.rb_proxy.GetItemLabel(self.rb_proxy.GetSelection())
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_Proxy, self.rb_proxy)
        self.proxyTextBtn = wx.Button(self, label='...', size=(30, 30))
        self.proxyTextBtn.Hide()
        self.Bind(wx.EVT_BUTTON, self.OnOpenProxyFile, self.proxyTextBtn)
        # 代理DNS，API, TXT配置输入框
        self.proxyText = wx.TextCtrl(self, -1, value=self.data.proxy_api, size=(247, 21))

        # 运行log
        om = wx.StaticBox(self, 0, "运行日志:")
        note = '''

        NOTE:
                1. 选择搜索关键词文件, 文件名必须为'kw.data';
                    点击生成模板按钮"+", 查看具体文件格式.
                2. 每个关键词可统一设置运行次数, 需先勾选该复选框.
                3. 选择H5执行方式, 需要点击按钮"+"来下载chromerdriver.
                    或者自行下载chromerdriver到文件夹: ~/chromerdriver
                4. 对于每个代理方式需配置对应请求地址或文件路径;
                    选择TXT方式, 需要点击按钮"..."来选择代理文件.
                5. 程序会在该app所在路径下生成日志文件: Result.txt

                                                                                                By: Liu Fei
        '''
        self.multiText = wx.TextCtrl(self, 0, value=note, size=(480, 275), style=wx.TE_MULTILINE|wx.TE_READONLY) #创建一个文本控件
        self.multiText.SetInsertionPoint(0)
        # 版权模块
        self.copyRight = wx.StaticText(self, 0, "©️LiuFei ┃ ✉️ lucaliufei@gmail.com")
        self.process = wx.StaticText(self, 0, "                                                                   ")
        # 运行按钮
        self.buttonRun = wx.Button(self, label="运行")
        self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.buttonRun)
        # 终止按钮
        self.buttonStop = wx.Button(self, label="关闭")
        self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.buttonStop)

        # 左侧布局
        mbox = wx.BoxSizer(wx.VERTICAL)
        vbox = wx.BoxSizer(wx.HORIZONTAL)
        leftbox = wx.BoxSizer(wx.VERTICAL)
        filebox = wx.StaticBoxSizer(fm, wx.HORIZONTAL)
        runBox = wx.StaticBoxSizer(rm, wx.HORIZONTAL)
        filebox.Add(self.kwText, 0, wx.ALIGN_LEFT, 5)
        filebox.Add(self.kwBtn, 0, wx.ALIGN_RIGHT, 5)
        filebox.Add(self.tmpBtn, 0, wx.ALIGN_RIGHT, 5)
        runBox.Add(self.runTime, 0, wx.ALL, 5)
        runBox.Add(self.runText, 0, wx.ALL, 5)
        leftbox.Add(filebox, 0, wx.ALL, 5)
        leftbox.Add(runBox, 0, wx.ALL, 5)
        driverbox = wx.StaticBoxSizer(dm, wx.HORIZONTAL)
        driverbox.Add(self.rb_platform, 0, wx.ALIGN_LEFT, 5)
        driverbox.Add(self.dndBtn, 0, wx.ALIGN_RIGHT, 5)
        leftbox.Add(driverbox, 0, wx.ALL, 5)
        proxyBox = wx.StaticBoxSizer(pm, wx.VERTICAL)
        proxymodBox = wx.BoxSizer(wx.HORIZONTAL)
        proxymodBox.Add(self.rb_proxy, 0, wx.ALIGN_LEFT, 5)
        proxymodBox.Add(self.proxyTextBtn, 0, wx.ALIGN_RIGHT, 5)
        proxyBox.Add(proxymodBox, 0, wx.ALL, 5)
        proxyBox.Add(self.proxyText,  0, wx.ALL, 5)
        leftbox.Add(proxyBox, 0, wx.ALL, 5)
        # 右侧布局
        rightBox = wx.BoxSizer(wx.VERTICAL)
        logBox = wx.StaticBoxSizer(om, wx.VERTICAL)
        logBox.Add(self.multiText, 0, wx.ALL, 5)
        rightBox.Add(logBox, 0, wx.ALL, 5)
        # 底部布局
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        btnBox.Add(self.copyRight, 0, wx.CENTER|wx.ALIGN_LEFT, 5)
        btnBox.Add(self.process, 0, wx.CENTER|wx.ALIGN_LEFT, 5)
        btnBox.Add(self.buttonRun, 0, wx.ALL, 5)
        btnBox.Add(self.buttonStop, 0, wx.ALL, 5)
        # 整体布局
        vbox.Add(leftbox, 0, wx.ALL|wx.ALL, 5)
        vbox.Add(rightBox, 0, wx.ALL|wx.ALL, 5)
        mbox.Add(vbox, 0, wx.ALL|wx.ALL, 5)
        mbox.Add(btnBox, 0, wx.CENTER|wx.CENTER, 5)
        self.SetSizer(mbox)

    def EvtRadioBox_PF(self, evt):
        # selected = self.rb_platform.GetItemLabel(self.rb_platform.GetSelection())
        # if selected == "H5-C":
        #     self.dndBtn.Show()
        #     self.Layout()
        # else:
        #     self.dndBtn.Hide()
        return self.rb_platform.GetItemLabel(self.rb_platform.GetSelection())

    def EvtCheckBox_RT(self, evt):
        if self.runTime.GetValue():
            self.runText.SetEditable(True)
        else:
            self.runText.SetEditable(False)

    def EvtRadioBox_Proxy(self, evt):
        self.proxyType = self.rb_proxy.GetItemLabel(self.rb_proxy.GetSelection())
        if self.proxyType == "API": self.OnClickAPI(evt)
        if self.proxyType == "DNS": self.OnClickDNS(evt)
        if self.proxyType == "TXT": self.OnClickTXT(evt)

    def OnClickAPI(self, evt):
        self.proxyText.SetValue(self.data.proxy_api)
        self.proxyText.SetEditable(True)
        self.proxyTextBtn.Hide()

    def OnClickDNS(self, evt):
        self.proxyText.SetValue(self.data.proxy_dns)
        self.proxyText.SetEditable(True)
        self.proxyTextBtn.Hide()

    def OnClickTXT(self, evt):
        self.proxyText.SetValue("点击右侧按钮选择文件...")
        self.proxyText.SetEditable(False)
        self.proxyTextBtn.Show()
        self.Layout()

    def OnClickRun(self, evt):
        # 添加drivers到环境变量
        os.system("export PATH=$PATH:%s" % self.dir)

        runtime = 0
        # 如果未选择keyworks文件, 提示错误
        if not self.keyworks:
            self.errInfo("请选择关键词配置文件!")
            return
        self.proxyConfig = self.proxyText.GetValue().strip()
        # 如果选择了固定运行次数, 但是赋值为空, 提示错误
        if self.runTime.GetValue():
            runtime = self.runText.GetValue().strip()
            if (not runtime) or (not runtime.isdigit()) or (not int(runtime)):
                self.errInfo("运行次数配置有误!")
                return
        # 如果代理配置为空, 提示错误
        if not self.proxyConfig:
            self.errInfo("代理设置不能为空!")
            return
        self.multiText.SetValue("")
        self.buttonRun.SetLabel("运行中")
        self.buttonStop.SetLabel("停止")
        evt.GetEventObject().Disable()
        from rank import rank
        drvierTyple = ""

        if self.EvtRadioBox_PF(evt).startswith('Web'): drvierTyple = "web_firefox"
        if self.EvtRadioBox_PF(evt).startswith('H5-C'): drvierTyple = "h5_chrome"
        if self.EvtRadioBox_PF(evt).startswith('H5-F'): drvierTyple = "h5_firefox"
        self.rankObj = rank(drvierTyple, self.proxyType, self.proxyConfig, self.keyworks, int(runtime))

    def OnClickStop(self, evt):
        ret = wx.MessageBox('确定要关闭吗?', '', wx.YES_NO)
        if ret == wx.YES:
            try:
                self.rankObj.end()
            except:
                pass
            wx.GetApp().ExitMainLoop()

    def OnOpenKWFile(self, evt):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "选择关键词文件....", os.getcwd(), style=wx.FC_OPEN, wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            kwfilename = dlg.GetPath()
            self.kwText.SetLabel(kwfilename)
            self.multiText.SetValue("")
            self.keyworks = self.kyFileHeadle(kwfilename)
            self.kwText.SetEditable(False)
        dlg.Destroy()

    def OnOpenProxyFile(self, evt):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "选择代理文件....", os.getcwd(), style=wx.FC_OPEN, wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            kwfilename = dlg.GetPath()
            self.proxyText.SetLabel(kwfilename)
            self.multiText.SetValue("")
        dlg.Destroy()

    def kyFileHeadle(self, filename):
        name = os.path.basename(filename)
        if name != "kw.data":
            self.errInfo("关键词文件名必须为: 'kw.data'")
            return False
        try:
            with open(filename, "r") as ff:
                kw = ff.read().decode("utf-8")
                return eval(kw)
        except Exception, e:
            self.errInfo("获取关键词文件失败:%s" % str(e))
            return False

    def cpDriver(self, evt):
        #下载并解压driver
        '''
        if self.EvtRadioBox_PF(evt) == "H5-C":
            downloadurl = "http://chromedriver.storage.googleapis.com/2.25/chromedriver_mac64.zip"
            file = "chromedriver_mac64.zip"
            filename = "/Users/%s/drivers/chromedriver_mac64.zip" % os.environ["USER"]
            # 通过wget下载
            try:
                os.system("wget -c -P %s %s" % (dir, downloadurl))
                self.errInfo("成功下载%s到目录: %s\n\n" % (file, dir))
            except Exception, e:
                self.errInfo("下载%s到目录'%s'失败 T_T, 请重试! Msg: " % (file, dir), True)
                self.errInfo(str(e)+"\n\n", True)
            # 解压下载文件
            import zipfile
            try:
                zfile = zipfile.ZipFile(filename)
                zfile.extractall(path=dir)
                self.errInfo("成功解压%s到目录: %s\n\n" % (file, dir), True)
            except Exception, e:
                self.errInfo("解压%s到目录'%s'失败 T_T, 请重试! Msg: " % (file, dir), True)
                self.errInfo(str(e)+"\n\n", True)
        else:
            downloadurl = "https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-macos.tar.gz"
            file = "geckodriver-v0.11.1-macos.tar.gz"
            filename = "/Users/%s/drivers/geckodriver-v0.11.1-macos.tar.gz" % os.environ["USER"]
            # 通过wget下载
            try:
                os.system("wget -c -P %s %s" % (dir, downloadurl))
                self.errInfo("成功下载%s到目录: %s\n\n" % (file, dir))
            except Exception, e:
                self.errInfo("下载%s到目录'%s'失败 T_T, 请重试! Msg: " % (file, dir), True)
                self.errInfo(str(e)+"\n\n", True)

            # 解压下载文件
            import tarfile
            try:
                tfile = tarfile.open(filename)
                tfile.extractall(path=dir)
                self.errInfo("成功解压%s到目录: %s\n\n" % (file, dir), True)
            except Exception, e:
                self.errInfo("解压%s到目录'%s'失败 T_T, 请重试! Msg: " % (file, dir), True)
                self.errInfo(str(e)+"\n\n", True)
                '''
        os.system("mkdir %s" % self.dir)
        try:
            import pkgutil, tarfile
            gdname = "geckodriver-v0.11.1-macos.tar.gz"
            cdname = "chromedriver_mac64.zip"
            cd = pkgutil.get_data('rank', gdname)
            gd = pkgutil.get_data('rank', cdname)
            if self.EvtRadioBox_PF(evt) == "H5-C":
                with open(self.dir+cdname, 'wb') as ff:
                    ff.write(cd)
                tfile = tarfile.open(cdname)
                tfile.extractall(path=self.dir)
                self.errInfo("成功解压%s到目录: %s\n\n" % (cdname, self.dir))
            else:
                with open(self.dir+gdname, 'wb') as ff:
                    ff.write(gd)
                tfile = tarfile.open(gdname)
                tfile.extractall(path=self.dir)
                self.errInfo("成功解压%s到目录: %s\n\n" % (gdname, self.dir))
        except Exception, e:
            self.errInfo(str(e))

    def OnCreateTmpFile(self, evt):
        kwconf = '''{
            #格式: {关键词:点击次数, 关键词:点击次数, ...}
            '曼谷旅游':10,
            '巴黎旅游':20,
        }'''
        try:
            with open("kw.data.tmp", "w") as ff:
                ff.write(kwconf)
            self.errInfo("已在当前目录下创建关键词模板文件: kw.data.tmp")
        except:
            self.errInfo("创建关键词模板文件失败!")

    def errInfo(self, log, mode=0):
            self.multiText.SetDefaultStyle(wx.TextAttr("RED"))
            if not mode:
                self.multiText.SetValue("\n\n" + log)
            else:
                self.multiText.AppendText(log)
            self.multiText.SetDefaultStyle(wx.TextAttr("BLACK"))

    def printLog(self, info):
        try:
            self.multiText.AppendText(info)
        except Exception, e:
            self.multiText.AppendText(str(e))

    def reset(self):
        self.buttonRun.Enable(True)
        self.buttonRun.SetLabel("运行")
        self.buttonStop.SetLabel("关闭")

    def update(self):
        pub.subscribe(self.errInfo, "log")
        pub.subscribe(self.printLog, "info")
        pub.subscribe(self.reset, "reset")

class rank(page, Thread):
    def __init__(self, driverType, proxyType, proxyConfig, keyworks, runtime=0):
        Thread.__init__(self)
        #搜索关键词
        self.driverType = driverType
        self.proxyType = proxyType
        self.proxyConfig = proxyConfig
        self.data = data()
        self.SearchKeywords = keyworks
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
        if self.driverType.startswith("web"):
            self.rank_baidu_web()
        if self.driverType.startswith("h5"):
            self.rank_baidu_m()
        wx.CallAfter(pub.sendMessage, "reset")
        wx.CallAfter(self.output_Result, log="[All Done]")

    def begin(self):
        # 实例化
        try:
            self.pageobj = page(self.driverType, self.proxyType, self.proxyConfig)
        except Exception, e:
            self.output_Result(info=str(e))
            wx.CallAfter(pub.sendMessage, "reset")
            exit()

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
            if not self.Runtime:
                value = kw[1]
            else:
                value = self.Runtime
            self.output_Result(info="【%d/%d】：当前关键词 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                self.output_Result(info="当前使用代理: %s" %self.pageobj.getProxyAddr())
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.pageobj.baidu)
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
                        for kw in self.data.URLKeywords:
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
            process += 1
            self.output_Result(info="当前关键词，成功点击%d次" % runtime)

    def rank_baidu_m(self):
        process = 1
        for kw in self.SearchKeywords.items():
            found = False   # 定位到关键词排名后，跳出循环标志位
            total = len(self.SearchKeywords)
            runtime = 0
            key = kw[0]
            if not self.Runtime:
                value = kw[1]
            else:
                value = self.Runtime
            self.output_Result(info="【%d/%d】：当前关键词 - %s" % (process, total, key))
            for click in range(value):
                self.begin()
                driver = self.pageobj.getDriver()
                self.output_Result(info="----------------------------------------------")
                self.output_Result(info="当前使用代理: %s" %self.pageobj.getProxyAddr())
                # 1. 打开搜索页面并使用关键词搜索
                try:
                    self.pageobj.gotoURL(self.pageobj.baidu_m)
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
                        for kw in self.data.URLKeywords:
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
            process += 1
            self.output_Result(info="当前关键词，成功点击%d次" % runtime)

if __name__ == "__main__":
    app = wx.App(False)
    frame = wx.Frame(None, title='刷百度排名小工具 v1.0', size=(800, 420), style=wx.MINIMIZE_BOX|wx.CLOSE_BOX)
    panel = wxRank(frame)
    frame.Show(True)
    app.MainLoop()