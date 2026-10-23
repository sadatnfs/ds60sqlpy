@echo off
setlocal DisableDelayedExpansion
where wsl.exe >nul 2>&1
if errorlevel 1 goto missing
wsl.exe --cd "%~dp0." --exec bash ./classroom %*
set "DS60_EXIT=%errorlevel%"
if "%DS60_EXIT%"=="0" exit /b 0
echo.
echo Classroom setup did not finish. Read the error above; saved volumes are retained.
echo Use an Ubuntu WSL 2 terminal with your Docker engine's WSL integration enabled.
echo See docs/one-command-classroom.md for first-time setup and recovery.
pause
exit /b %DS60_EXIT%
:missing
echo Install WSL 2 and Ubuntu, then enable your Docker engine's integration for Ubuntu.
echo See docs/one-command-classroom.md. No engine or distribution was changed.
pause
exit /b 2
