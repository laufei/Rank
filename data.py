# coding: utf-8
__author__ = 'liufei'
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class data:
    def __init__(self):
        self.baidu_url = "https://www.baidu.com/"
        self.baidu_url_request_web = "https://www.baidu.com/s?wd=%s&pn=%d&rsv_spt=1&issp=1&f=8&rsv_bp=0&rsv_idx=2&ie=utf-8&tn=baiduhome_pg&rsv_enter=0&rsv_sug3=16&rsv_sug1=18&rsv_sug7=101&inputT=6882&rsv_sug4=8327&rsv_sug=1"
        self.baidu_url_request_m = "https://m.baidu.com/s?word=%s&pn=%d&ref=www_colorful&st=111041&from=1014994a"
        self.sm_url = "http://m.sm.cn/"
        self.sogou_url = "https://www.sogou.com/"
        self.proxy_dns = "http://127.0.0.1:8000/?types=0&count=500"
        self.proxy_api = "http://api.xicidaili.com/free2016.txt"
        self.proxy_txt = "proxy.txt"