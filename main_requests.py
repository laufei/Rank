# coding: utf-8
__author__ = 'liufei'

import wx
from rank_req.wxrank_requests import wxRank_requests

if __name__ == "__main__":
    app = wx.App()
    wxRank_requests()
    app.MainLoop()