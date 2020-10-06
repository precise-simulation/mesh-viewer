# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['meshviewer_vispy_tk.py'],
             pathex=['C:\\Users\\jshysing\\Dropbox\\code\\python\\meshviewer'],
             binaries=[],
             datas=[],
             hiddenimports=['vispy.ext._bundled.six'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='meshviewer_vispy_tk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='meshviewer_vispy_tk')
