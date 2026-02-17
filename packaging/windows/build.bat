@echo off
REM Build DupPicFinder for Windows
REM Run this script from a Windows machine or Windows VM after cloning the repo.
REM
REM Prerequisites:
REM   - Python 3.10+ installed and on PATH (https://www.python.org/downloads/)
REM   - Git for Windows (to clone the repo)
REM
REM Output: dist\DupPicFinder.exe

setlocal enabledelayedexpansion

echo ====================================================
echo   Building DupPicFinder - Windows Build
echo   Target: Windows 10 / 11 (x64)
echo ====================================================
echo.

REM Move to the project root (two levels up from packaging\windows\)
cd /d "%~dp0..\.."
set PROJECT_ROOT=%CD%

echo Project root: %PROJECT_ROOT%
echo.

REM Check Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found on PATH.
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo Python: %%v

REM Create virtual environment if it doesn't exist
if not exist "%PROJECT_ROOT%\venv" (
    echo Creating virtual environment...
    python -m venv "%PROJECT_ROOT%\venv"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    exit /b 1
)

REM Install / upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip --quiet
pip install -r "%PROJECT_ROOT%\requirements.txt" --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    exit /b 1
)

REM Install PyInstaller
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    exit /b 1
)

REM Clean previous build output
echo Cleaning previous build artifacts...
if exist "%PROJECT_ROOT%\build" rd /s /q "%PROJECT_ROOT%\build"
if exist "%PROJECT_ROOT%\dist\DupPicFinder.exe" del /f /q "%PROJECT_ROOT%\dist\DupPicFinder.exe"

REM Run PyInstaller
echo.
echo Building executable with PyInstaller...
echo.
cd /d "%PROJECT_ROOT%"
pyinstaller --clean DupPicFinder.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. Check the output above for details.
    exit /b 1
)

REM Verify output
if exist "%PROJECT_ROOT%\dist\DupPicFinder.exe" (
    echo.
    echo Build successful!
    echo.
    for %%f in ("%PROJECT_ROOT%\dist\DupPicFinder.exe") do (
        echo   File: %%~nxf
        echo   Size: %%~zf bytes
        echo   Path: %%~ff
    )
    echo.
    echo To run:
    echo   dist\DupPicFinder.exe
) else (
    echo.
    echo ERROR: Build failed - DupPicFinder.exe not found in dist\.
    exit /b 1
)

endlocal
