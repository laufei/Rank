# coding: utf-8
__author__ = 'liufei'

import wx
from rank.wxrank import wxRank

if __name__ == "__main__":
    app = wx.App()
    wxRank()
    app.MainLoop()