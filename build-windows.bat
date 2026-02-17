@echo off
REM Convenience wrapper — delegates to packaging\windows\build.bat
REM Run from the project root on a Windows machine:
REM   build-windows.bat
call "%~dp0packaging\windows\build.bat"
