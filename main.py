# coding: utf-8
__author__ = 'liufei'

from rank import rank
import unittest

for i in range(120):
    test_suite = unittest.TestSuite()
    test_suite.addTest(rank("test_rank_baidu"))
    unittest.TextTestRunner(verbosity=2).run(test_suite)