__author__ = 'liufei'
import os
# os.system("pyinstaller -F -w --icon='../src/icon.ico' ../rank/rank.py")      # for mac
# os.system("pyinstaller -F -w --onefile --icon='../src/icon.ico' ../rank_req/wxrank_requests.py")        # for windows
# os.system("pyinstaller --onefile -y rank/rank_mac.spec")
# os.system("pyinstaller --onefile -y rank/rank_win.spec")
os.system("pyinstaller --onefile -y rank_req/rank_requests_mac.spec")
# os.system("pyinstaller --onefile -y ../rank_req/rank_requests_win.spec")
