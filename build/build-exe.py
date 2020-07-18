"""
This is an example of using PyInstaller packager to build
an executable for meshviewer with plotly/cef.

Adapted from https://github.com/cztomczak/cefpython/tree/master/examples/pyinstaller

To package example type: `python build-pyinstaller.py`.
"""

import os
import platform
import shutil
import sys
from subprocess import Popen

try:
    import PyInstaller
except ImportError:
    PyInstaller = None
    raise SystemExit("Error: PyInstaller package missing. "
                     "To install type: pip install --upgrade pyinstaller")

APP = "meshviewer"

EXE_EXT = ""
if platform.system() == "Windows":
    EXE_EXT = ".exe"
elif platform.system() == "Darwin":
    EXE_EXT = ".app"
elif platform.system() == "Linux":
    EXE_EXT = ""


def main():
    # Platforms supported
    if platform.system() not in ["Windows", "Darwin", "Linux"]:
        raise SystemExit("Error: Only Windows, Linux and Darwin platforms are "
                         "currently supported. See Issue #135 for details.")

    # Make sure nothing is cached from previous build.
    # Delete the build/ and dist/ directories.
    if os.path.exists("build/"):
        shutil.rmtree("build/")
    if os.path.exists("dist/"):
        shutil.rmtree("dist/")

    # Execute pyinstaller.
    # Note: the "--clean" flag passed to PyInstaller will delete
    #       global global cache and temporary files from previous
    #       runs. For example on Windows this will delete the
    #       "%appdata%/roaming/pyinstaller/bincache00_py27_32bit"
    #       directory.
    env = os.environ
    if "--debug" in sys.argv:
        env["CEFPYTHON_PYINSTALLER_DEBUG"] = "1"
    sub = Popen(["pyinstaller", "--clean", "meshviewer_plotly_cef_tk.spec"], env=env)
    sub.communicate()
    rcode = sub.returncode
    if rcode != 0:
        print("Error: PyInstaller failed, code=%s" % rcode)
        # Delete distribution directory if created
        if os.path.exists("dist/"):
            shutil.rmtree("dist/")
        sys.exit(1)

    # Make sure everything went fine
    curdir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(curdir, "dist")
    executable = os.path.join(app_dir, APP+EXE_EXT)
    if not os.path.exists(executable):
        print("Error: PyInstaller failed, main executable is missing: %s"
              % executable)
        sys.exit(1)

    # Done
    print("OK. Created dist/ directory.")

    # On Windows open folder in explorer or when --debug is passed
    # run the result binary using "cmd.exe /k app.exe", so that
    # console window doesn't close.
    if platform.system() == "Windows":
        if "--debug" in sys.argv:
            os.system("start cmd /k \"%s\"" % executable)
        else:
            # SYSTEMROOT = C:/Windows
            os.system("%s/explorer.exe /n,/e,%s" % (
                os.environ["SYSTEMROOT"], app_dir))


if __name__ == "__main__":
    main()
