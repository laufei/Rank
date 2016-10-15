# coding: utf-8
__author__ = 'liufei'
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class data:
    def __init__(self):
        self.proxy_dns = "d.conn.run:32804"
        self.proxy_api = "http://www.shandiandaili.com/bindip.aspx?Key=f01064e025ce0a6717db03a8bc4f2712&IP=60.206.194.34"
        self.proxy_txt = "proxy.txt"
        self.URLKeywords = [u'穷游网']
        self.SearchKeywords = {
                                                u'曼谷旅游':20,
                                                u'新加坡旅游':117,
                                                u'清迈旅游':17,
                                                u'大阪旅游':17,
                                                u'首尔旅游': 38,
                                                u'马来西亚旅游':105,
                                                u'纽约旅游':56,
                                                u'荷兰旅游':19,
                                                u'意大利旅游':29
        }
