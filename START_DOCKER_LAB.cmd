@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\docker_lab.ps1" %*
set "DS60_DOCKER_EXIT=%ERRORLEVEL%"
if not "%DS60_DOCKER_EXIT%"=="0" pause
exit /b %DS60_DOCKER_EXIT%
