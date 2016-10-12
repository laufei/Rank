# coding: utf-8
__author__ = 'liufei'
from distutils.core import setup
import py2exe

setup(
    windows=['rank.py'],
    options={'py2exe': {"dll_excludes": ["MSVCP90.dll"]}},
    data_files=[('', ['proxy.txt'])]
)