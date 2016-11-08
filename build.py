__author__ = 'liufei'
import os
# os.system("pyinstaller -F -w --icon='src/icon.ico' rank.py")      # for mac
# os.system("pyinstaller --onedir -y rank_mac.spec")
os.system("pyinstaller --onedir -y rank_win.spec")