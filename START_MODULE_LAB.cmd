@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\module_lab.ps1" start -Interactive
if errorlevel 1 pause
endlocal
