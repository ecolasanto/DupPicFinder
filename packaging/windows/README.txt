DupPicFinder — Windows Build
============================

This directory contains the script for building a native Windows executable
using PyInstaller.  PyInstaller must run ON Windows to produce a .exe — it
cannot cross-compile from Linux or macOS.


Prerequisites
-------------
1. Python 3.10 or newer
   https://www.python.org/downloads/
   ✔ Check "Add Python to PATH" during installation.

2. Git for Windows (to clone the repository)
   https://git-scm.com/download/win


Quick Start
-----------
1. Open a Command Prompt (cmd.exe) or PowerShell window.

2. Clone the repository (if you haven't already):
     git clone https://github.com/ecolasanto/DupPicFinder.git
     cd DupPicFinder

3. Run the build script:
     packaging\windows\build.bat

4. The finished executable will be at:
     dist\DupPicFinder.exe

5. Double-click dist\DupPicFinder.exe to launch the application.
   No Python installation is required on the end-user machine.


What the Script Does
--------------------
  • Creates a Python virtual environment in venv\
  • Installs all dependencies from requirements.txt
  • Installs PyInstaller
  • Runs: pyinstaller --clean DupPicFinder.spec
  • Produces:  dist\DupPicFinder.exe  (single-file, no console window)


Cache Location on Windows
--------------------------
The hash cache database is stored at:
  %LOCALAPPDATA%\DupPicFinder\hash_cache.db

Typically this resolves to:
  C:\Users\<YourName>\AppData\Local\DupPicFinder\hash_cache.db

Delete this file to force a full re-hash on the next run.


Troubleshooting
---------------
"Python not found on PATH"
  → Re-install Python and make sure "Add Python to PATH" is checked.
  → Or add Python manually: Settings → System → Advanced → Environment Variables.

"pip install failed" / SSL errors
  → Run:  python -m pip install --upgrade pip
  → Then re-run build.bat.

"pyinstaller: command not found" after venv activation
  → The venv activation may have failed.  Try running from a fresh cmd window.

PyQt5 import errors at runtime
  → Make sure you are NOT mixing a system PyQt5 with the venv PyQt5.
  → Delete venv\ and re-run build.bat to get a clean environment.

HEIC images not loading
  → pillow-heif wheels are available on PyPI for Windows; they are installed
    automatically via requirements.txt.  No extra steps needed.


Alternative: GitHub Actions (No Windows Machine Required)
----------------------------------------------------------
See .github/workflows/build-windows.yml for an automated build that runs on
GitHub's hosted Windows runners and uploads DupPicFinder.exe as a release
artifact on every tagged push.
