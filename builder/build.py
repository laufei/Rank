__author__ = 'liufei'
import os
# os.system("pyinstaller -F -w --icon='../src/icon.ico' ../rank/rank.py")      # for mac
#os.system("pyinstaller -F -w --icon='../src/icon.ico' ../rank_req/rank_requests.py")         # for mac
# os.system("pyinstaller --onedir -y rank/rank_mac.spec")
os.system("pyinstaller --onedir -y rank_req/rank_requests.spec")
# os.system("pyinstaller --onedir -y rank/rank_win.spec")