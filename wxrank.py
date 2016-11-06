# coding: utf-8
__author__ = 'liufei'

import os, wx, platform
from page import page
from data import data
from wx.lib.pubsub import pub

class wxRank(wx.Frame, page):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='刷搜索排名小工具 v1.0', size=(840, 520), style=wx.MINIMIZE_BOX|wx.CLOSE_BOX)
        self.data = data()
        self.keyworks, self.proxyType, self.proxyConfig = "", "", ""
        self.proValue, self.spend = 0, 0
        self.update()
        self.Bind(wx.EVT_CLOSE, self.OnClickStop)
        # 创建定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        # 添加drivers到环境变量
        if platform.system() == "Darwin":
            self.dir = "%s/drivers/" % os.environ["HOME"]
        elif platform.system() == "Windows":
            self.dir = "%s\\drivers" % os.environ["USERPROFILE"]
        os.environ["PATH"] += ':' + self.dir

        self.note = u'''


        1. 运行平台:
            需安装对应浏览器(F=Firefox, C=Chrome);
            第一次使用需人肉点击"+"按钮配置必须的driver及环境变量.
        2. 关键词文件路径:
            文件名须为'kw.data'; 点击生成模板按钮"+", 查看具体文件格式.
        3. 运行次数:
            勾选了该复选框, 每个关键词运行次数被统一配置.
        4. 代理方式:
            对于每个代理方式需配置对应请求地址或文件路径;
            如选择TXT方式, 需要点击按钮"..."来选择代理文件.
        5. 运行日志:
            程序执行过程中会输入log信息, 包括各种报错及提示信息
            程序会在该app所在路径下生成日志文件: Result.txt
        '''
        self.font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        # 选择搜索引擎: baidu, sm, sogou
        sm = wx.StaticBox(self, -1, u"搜索平台:")
        # self.runType = wx.ToggleButton(self, -1, "读", size=(30, 21))
        spfList = ["Baidu", "SM", "Sogou"]
        self.rb_splatform = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, spfList, 3)
        # 选择平台：web，h5
        dm = wx.StaticBox(self, -1, u"运行平台:")
        pfList = ["H5-F", "H5-C", "Web-F"]
        self.rb_platform = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, pfList, 3)
        self.dndBtn = wx.Button(self, label='+', size=(30, 30))
        self.Bind(wx.EVT_BUTTON, self.cpDriver, self.dndBtn)
        # 选择keywords文件
        fm = wx.StaticBox(self, -1, u"关键词文件路径:")
        self.kwText = wx.TextCtrl(self, -1, value=u"点击右侧按钮选择文件...", size=(198, 21))
        self.kwText.Disable()
        self.kwText.SetFont(self.font)
        # self.kwText.SetEditable(False)
        self.kwBtn = wx.Button(self, label='...', size=(30, 21))
        self.Bind(wx.EVT_BUTTON, self.OnOpenKWFile, self.kwBtn)
        self.tmpBtn = wx.Button(self, label='+', size=(30, 21))
        self.Bind(wx.EVT_BUTTON, self.OnCreateTmpFile, self.tmpBtn)
        # 关键词运行次数
        rm = wx.StaticBox(self, -1, u"运行次数:")
        self.runTime = wx.CheckBox(self, -1, u"是否统一配置?  运行次数:")
        self.runText = wx.TextCtrl(self, -1, size=(65, 21))
        self.runText.SetEditable(False)
        self.runText.SetValue("10")
        self.Bind(wx.EVT_CHECKBOX, self.EvtCheckBox_RT, self.runTime)
        # 选择代理方式：dns, api，txt
        pm = wx.StaticBox(self, -1, u"代理方式:")
        sampleList = ["API", "DNS", "TXT"]
        self.rb_proxy = wx.RadioBox(self, -1, "", wx.DefaultPosition, wx.DefaultSize, sampleList, 3)
        self.proxyType = self.rb_proxy.GetItemLabel(self.rb_proxy.GetSelection())
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox_Proxy, self.rb_proxy)
        self.proxyTextBtn = wx.Button(self, label='...', size=(30, 30))
        self.proxyTextBtn.Hide()
        self.Bind(wx.EVT_BUTTON, self.OnOpenProxyFile, self.proxyTextBtn)
        # 代理DNS，API, TXT配置输入框
        self.proxyText = wx.TextCtrl(self, -1, value=self.data.proxy_api, size=(247, 21))
        self.proxyText.SetFont(self.font)

        # 运行log
        om = wx.StaticBox(self, -1, u"运行日志:")
        self.multiText = wx.TextCtrl(self, -1, value=self.note, size=(480, 360), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.multiText.SetInsertionPoint(0)
        # 版权模块
        self.copyRight = wx.StaticText(self, -1, u"©️LiuFei ┃ lucaliufei@gmail.com", style=1)
        self.spendTime = wx.StaticText(self, -1, u"耗时: [--:--:--]  ")
        self.proText = wx.StaticText(self, -1, u"进度:")
        self.process = wx.Gauge(self, -1, size=(200, 20), style=wx.GA_HORIZONTAL)
        self.Bind(wx.EVT_IDLE, self.Onprocess)
        # 运行按钮
        self.buttonRun = wx.Button(self, label=u"运行")
        self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.buttonRun)
        # 终止按钮
        self.buttonStop = wx.Button(self, label=u"关闭")
        self.Bind(wx.EVT_BUTTON, self.OnClickStop, self.buttonStop)

        # 左侧布局
        mbox = wx.BoxSizer(wx.VERTICAL)
        vbox = wx.BoxSizer(wx.HORIZONTAL)
        leftbox = wx.BoxSizer(wx.VERTICAL)
        searchbox = wx.StaticBoxSizer(sm, wx.HORIZONTAL)
        # searchbox.Add(self.runType, 0, wx.ALL|wx.CENTER, 1)
        searchbox.Add(self.rb_splatform, 0, wx.ALL, 5)
        driverbox = wx.StaticBoxSizer(dm, wx.HORIZONTAL)
        driverbox.Add(self.rb_platform, 0, wx.ALIGN_LEFT, 5)
        driverbox.Add(self.dndBtn, 0, wx.ALIGN_RIGHT, 5)
        filebox = wx.StaticBoxSizer(fm, wx.HORIZONTAL)
        filebox.Add(self.kwText, 0, wx.ALIGN_LEFT, 5)
        filebox.Add(self.kwBtn, 0, wx.ALIGN_RIGHT, 5)
        filebox.Add(self.tmpBtn, 0, wx.ALIGN_RIGHT, 5)
        runBox = wx.StaticBoxSizer(rm, wx.HORIZONTAL)
        runBox.Add(self.runTime, 0, wx.ALL, 5)
        runBox.Add(self.runText, 0, wx.ALL, 5)
        leftbox.Add(searchbox, 0, wx.ALL, 5)
        leftbox.Add(driverbox, 0, wx.ALL, 5)
        leftbox.Add(filebox, 0, wx.ALL, 5)
        leftbox.Add(runBox, 0, wx.ALL, 5)
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
        buttomBox = wx.BoxSizer(wx.HORIZONTAL)
        processBox = wx.BoxSizer(wx.HORIZONTAL)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        processBox.Add(self.copyRight, 0, wx.ALL, 5)
        processBox.Add(self.spendTime, 0, wx.ALL, 5)
        processBox.Add(self.proText, 0, wx.ALL, 5)
        processBox.Add(self.process, 0, wx.ALL, 5)
        btnBox.Add(self.buttonRun, 0, wx.ALL, 5)
        btnBox.Add(self.buttonStop, 0, wx.ALL, 5)
        # 整体布局
        vbox.Add(leftbox, 0, wx.ALL, 5)
        vbox.Add(rightBox, 0, wx.ALL, 5)
        buttomBox.Add(processBox, 0, wx.ALL, 5)
        buttomBox.Add(btnBox, 0, wx.ALL, 5)
        mbox.Add(vbox, 0, wx.ALL, 5)
        mbox.Add(buttomBox, 0, wx.ALL, 5)

        self.SetSizer(mbox)
        self.Show()

    def OnStart(self):
        self.timer.Start(1000)

    def OnStop(self):
        self.timer.Stop()

    def OnTimer(self, evt):
        self.spend += 1
        hour = str(self.spend/3600)
        min = str((self.spend % 3600)/60)
        sec = str(self.spend % 3600 % 60)
        self.spendTime.SetLabel(u"耗时: [%s:%s:%s]" % (
            "".join(["0", hour]) if int(hour) < 10 else hour,
            min if int(min) >= 10 else "".join(["0", min]),
            sec if int(sec) >= 10 else "".join(["0", sec])
        ))

    def EvtRadioBox_PF(self, evt):
        return self.rb_platform.GetSelection()

    def EvtRadioBox_SPF(self, evt):
        return self.rb_splatform.GetSelection()

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

    def getProcess(self, value):
        self.proValue = value

    def Onprocess(self, evt):
        self.process.SetValue(self.proValue)

    def DisableOnRun(self):
        self.rb_splatform.Disable()
        self.rb_platform.Disable()
        self.dndBtn.Disable()
        self.kwBtn.Disable()
        self.tmpBtn.Disable()
        self.runTime.Disable()
        self.runText.Disable()
        self.rb_proxy.Disable()
        self.proxyTextBtn.Disable()
        self.proxyText.Disable()

    def EnableOnStop(self):
        self.rb_splatform.Enable()
        self.rb_platform.Enable()
        self.dndBtn.Enable()
        self.kwBtn.Enable()
        self.tmpBtn.Enable()
        self.runTime.Enable()
        self.runText.Enable()
        self.rb_proxy.Enable()
        self.proxyTextBtn.Enable()
        self.proxyText.Enable()

    def OnClickAPI(self, evt):
        self.proxyText.Enable()
        self.proxyText.SetValue(self.data.proxy_api)
        self.proxyText.SetEditable(True)
        self.proxyTextBtn.Hide()

    def OnClickDNS(self, evt):
        self.proxyText.Enable()
        self.proxyText.SetValue(self.data.proxy_dns)
        self.proxyText.SetEditable(True)
        self.proxyTextBtn.Hide()

    def OnClickTXT(self, evt):
        self.proxyText.Disable()
        self.proxyText.SetValue(u"点击右侧按钮选择文件...")
        self.proxyTextBtn.Show()
        self.Layout()

    def OnClickRun(self, evt):
        runtime = 0
        # 如果未选择keyworks文件, 提示错误
        if not self.keyworks:
            self.errInfo(u"请选择关键词配置文件!")
            return
        self.proxyConfig = self.proxyText.GetValue().strip()
        # 如果选择了固定运行次数, 但是赋值为空, 提示错误
        if self.runTime.GetValue():
            runtime = self.runText.GetValue().strip()
            if (not runtime) or (not runtime.isdigit()) or (not int(runtime)):
                self.errInfo(u"运行次数配置有误!")
                return
        # 如果代理配置为空, 提示错误
        if self.proxyConfig == "" or self.proxyConfig == u"点击右侧按钮选择文件...":
            self.errInfo(u"代理设置不能为空!")
            return
        self.multiText.SetValue("")
        self.buttonRun.SetLabel(u"运行中")
        self.buttonStop.SetLabel(u"停止")
        evt.GetEventObject().Disable()
        self.DisableOnRun()
        self.OnStart()

        from rank import rank
        searcher = self.EvtRadioBox_SPF(evt)
        drvierType = self.EvtRadioBox_PF(evt)
        self.rankObj = rank(searcher, drvierType, self.proxyType, self.proxyConfig, self.keyworks, int(runtime))

    def OnClickStop(self, evt):
        ret = wx.MessageBox(u"确定要关闭吗?", "", wx.YES_NO)
        if ret == wx.YES:
            try:
                self.rankObj.end()
            except:
                pass
            self.Destroy()
            wx.GetApp().ExitMainLoop()

    def OnOpenKWFile(self, evt):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择关键词文件....", os.getcwd(), style=wx.FC_OPEN, wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            kwfilename = dlg.GetPath()
            self.kwText.SetLabel(kwfilename)
            self.multiText.SetValue(self.note)
            self.keyworks = self.kyFileHeadle(kwfilename)
            self.kwText.SetEditable(False)
        dlg.Destroy()

    def OnOpenProxyFile(self, evt):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, u"选择代理文件....", os.getcwd(), style=wx.FC_OPEN, wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            kwfilename = dlg.GetPath()
            self.proxyText.SetLabel(kwfilename)
            self.proxyConfig = kwfilename
            self.multiText.SetValue(self.note)
        dlg.Destroy()

    def kyFileHeadle(self, filename):
        name = os.path.basename(filename)
        if name != "kw.data":
            self.errInfo(u"关键词文件名必须为: 'kw.data'")
            return False
        try:
            with open(filename, "r") as ff:
                kw = ff.read().decode("utf-8")
                return eval(kw)
        except Exception, e:
            self.errInfo(u"获取关键词文件失败:%s" % str(e))
            return False

    def cpDriver(self, evt):
        os.system("mkdir %s" % self.dir)
        import pkgutil, tarfile
        cdname = "chromedriver_mac64.tar.gz"
        cd = pkgutil.get_data('rank', cdname)
        cdpath = self.dir + cdname
        gdname = "geckodriver-v0.11.1-macos.tar.gz"
        gd = pkgutil.get_data('rank', gdname)
        gdpath = self.dir + gdname
        try:
            if self.EvtRadioBox_PF(evt) == "H5-C":
                with open(cdpath, 'wb') as ff:
                    ff.write(cd)
                zfile = tarfile.open(cdpath)
                zfile.extractall(path=self.dir)
                self.errInfo(u"成功解压%s到目录: %s\n\n" % (cdname, self.dir))
            else:
                with open(gdpath, 'wb') as ff:
                    ff.write(gd)
                tfile = tarfile.open(gdpath)
                tfile.extractall(path=self.dir)
                self.errInfo(u"成功解压%s到目录: %s\n\n" % (gdname, self.dir))
        except Exception, e:
            self.errInfo(str(e))

    def OnCreateTmpFile(self, evt):
        kwconf = u'''{
            #格式: {关键词:点击次数, 关键词:点击次数, ...}
            '曼谷旅游':10,
            '巴黎旅游':20,
        }'''
        try:
            with open("kw.data.tmp", "w") as ff:
                ff.write(kwconf)
            self.errInfo(u"已在当前目录下创建关键词模板文件: kw.data.tmp")
        except:
            self.errInfo(u"创建关键词模板文件失败!")

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
        self.EnableOnStop()
        self.buttonRun.Enable(True)
        self.buttonRun.SetLabel(u"运行")
        self.buttonStop.SetLabel(u"关闭")
        self.OnStop()

    def update(self):
        pub.subscribe(self.errInfo, "log")
        pub.subscribe(self.printLog, "info")
        pub.subscribe(self.reset, "reset")
        pub.subscribe(self.getProcess, "process")

if __name__ == "__main__":
    app = wx.App()
    wxRank()
    app.MainLoop()