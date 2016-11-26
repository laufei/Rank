# coding: utf-8
__author__ = 'liufei'
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class data:
    def __init__(self):
        self.baidu_url = "https://www.baidu.com/"
        self.baidu_url_request = "https://www.baidu.com/s?word=%s&pn=%d"
        self.sm_url = "http://m.sm.cn/"
        self.sogou_url = "https://www.sogou.com/"
        self.proxy_dns = "d.conn.run:32804"
        self.proxy_api = "http://url.cn/412TnYr"
        self.URLKeywords = [u'穷游网']
