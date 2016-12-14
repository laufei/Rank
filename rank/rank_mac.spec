# -*- mode: python -*-

block_cipher = None
APP_NAME = 'Ranker'
added_files = [
            ('../drivers/geckodriver-v0.11.1-macos.tar.gz', 'rank/drivers'),
            ('../drivers/phantomjs-2.1.1-macosx.tar.gz', 'rank/drivers'),
            ('../src', 'src')
            ]
a = Analysis(['../main.py'],
             pathex=['/Users/luca/PycharmProjects/Rank'],
             binaries=None,
             datas=added_files,
             hiddenimports=["selenium", "requests"],
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
             name='Ranker v1.0.app',
             icon='../src/icon.ico',
             bundle_identifier=None,
             info_plist={
                'CFBundleName': APP_NAME,
                'CFBundleDisplayName': APP_NAME,
                'CFBundleGetInfoString': "Making rank",
                'CFBundleVersion': "1.0",
                'CFBundleShortVersionString': "1.0",
                'NSHumanReadableCopyright': "Copyright © 2016, liufei, All Rights Reserved",
                'NSHighResolutionCapable': 'True',
                }
             )