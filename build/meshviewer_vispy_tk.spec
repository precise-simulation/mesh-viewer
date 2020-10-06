# -*- mode: python -*-
# -*- coding: utf-8 -*-

"""
This is a PyInstaller spec file.
"""

import os
import sys
from PyInstaller.building.api import PYZ, EXE
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import is_module_satisfies
from PyInstaller.archive.pyz_crypto import PyiBlockCipher
import vispy.glsl
import vispy.io

# Constants
DEBUG = "--debug" in sys.argv
ONEFILE = "--onefile" in sys.argv

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

data_files = [
    (os.path.dirname(vispy.glsl.__file__), os.path.join("vispy", "glsl")),
    (os.path.join(os.path.dirname(vispy.io.__file__), "_data"), os.path.join("vispy", "io", "_data"))
]

hidden_imports = [
    "vispy.ext._bundled.six",
    "vispy.app.backends._tk"]

a = Analysis(
    ["../meshviewer_vispy_tk.py"],
    hookspath=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    win_private_assemblies=True,
    win_no_prefer_redirects=True,
)

pyz = PYZ(a.pure,
          a.zipped_data)

if ONEFILE:
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name="meshviewer",
              debug=DEBUG,
              strip=False,
              upx=False,
              console=DEBUG,
              icon=False)
else:
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name="meshviewer",
              debug=DEBUG,
              strip=False,
              upx=False,
              console=DEBUG)

    COLLECT(exe,
            a.binaries,
            a.zipfiles,
            a.datas,
            strip=False,
            upx=False,
            name="meshviewer")
