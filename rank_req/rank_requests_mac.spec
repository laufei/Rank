# -*- mode: python -*-

block_cipher = None
APP_NAME = 'Ranker v2.0'
added_files = [
            ('../src', 'src')
            ]
a = Analysis(['../main_requests.py'],
             pathex=['/Users/luca/PycharmProjects/Rank'],
             binaries=None,
             datas=added_files,
             hiddenimports=["BeautifulSoup", "requests"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Ranker',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='../src/icon.ico')

app = BUNDLE(exe,
             name='Ranker v2.0.app',
             icon='../src/icon.ico',
             bundle_identifier=None,
             info_plist={
                'CFBundleName': APP_NAME,
                'CFBundleDisplayName': APP_NAME,
                'CFBundleGetInfoString': "Making rank",
                'CFBundleVersion': "2.0",
                'CFBundleShortVersionString': "2.0",
                'NSHumanReadableCopyright': "Copyright © 2016, liufei, All Rights Reserved",
                'NSHighResolutionCapable': 'True',
                }
             )
