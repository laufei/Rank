# coding: utf-8
__author__ = 'liufei'

import unittest, time, random
from page import page
from selenium.webdriver.common.by import By

class rank(unittest.TestCase, page):
    def setUp(self):
        # 实例化
        self.pageobj = page()
        self.data = self.pageobj.data

        # 常量设置
        self.PagesCount = 2     # 搜索结果页面中，遍历结果页面数量
        self.randomNo_firstpage = 2  # 首页最大随机点击URL数量
        self.radio_sorted = 0.8  # 首页正序随机点击URL比例

        # 记录Error数量
        self.verificationErrors = []

    def tearDown(self):
        self.pageobj.quit()
        self.assertEqual([], self.verificationErrors)

    def test_rank_baidu(self):
        driver = self.pageobj.getDriver()
        # 1. 打开搜索页面并使用关键词搜索
        self.pageobj.gotoURL(self.data.baidu)
        self.pageobj.isPageOpened(*self.baidu_kw)
        window = driver.current_window_handle
        self.pageobj.find_element(*self.baidu_kw).send_keys(self.data.SearchKeywords)
        self.pageobj.find_element(*self.baidu_submit).click()
        time.sleep(2)

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
                    targets = sorted(random.sample(range(5), random.sample(range(1, self.randomNo_firstpage+1), 1)[0]))
                else:
                    targets = random.sample(range(5), random.sample(range(1, self.randomNo_firstpage+1), 1)[0])
                for index in targets:
                    print "         点击结果页面第[%d]个链接" % (index+1)
                    baidu_result_items[index].click()
                    driver.switch_to_window(window)
            else:
                pageButton[page].click()
                time.sleep(3)
                # 等待翻页数据加载完成
                self.pageobj.waitForPageLoad(*self.baidu_kw)

            # 3. 遍历结果页面中的跳转URL，并点击结果URL
            baidu_result_items = self.pageobj.find_elements(*self.baidu_result_items)
            for index in range(len(baidu_result_items)):
                resultTitle = baidu_result_items[index].text
                resultURL = baidu_result_items[index].get_attribute("href")
                for key in self.data.URLKeywords:
                    if key in resultTitle:
                        print "         点击结果页面第[%d]个链接: %s" % (index+1, resultURL)
                        baidu_result_items[index].click()
                        time.sleep(2)
                    driver.switch_to_window(window)
                self.pageobj.scroll_page(100)
        self.output_testResult(self.pageobj.getProxyAddr())

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(rank("test_rank_baidu"))

    unittest.TextTestRunner(verbosity=2).run(test_suite)