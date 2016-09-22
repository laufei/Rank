# coding: utf-8
__author__ = 'liufei'

import sys
from selenium.webdriver.common.by import By
from base import base
reload(sys)
sys.setdefaultencoding('utf8')

class page(base):
    def __init__(self):
        self.baidu_kw = (By.ID, 'kw')                # 百度首页输入框
        self.baidu_submit = (By.ID, 'su')                # 百度首页搜索button
        self.baidu_result_pages = (By.CSS_SELECTOR, 'span.pc')       # 百度搜索结果页面中翻页控件
        self.baidu_result_items = (By.CSS_SELECTOR, 'h3.t a') # 百度搜索结果页面中搜索结果模块
        self.baidu_result_item = '(By.ID, "{id}")'    # 百度搜索结果页面中搜索结果模块
        self.baidu_result_url = (By.CSS_SELECTOR, 'h3.t a')      # 百度搜索结果页面中搜索结果模块URL
