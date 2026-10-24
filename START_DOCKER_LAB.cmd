@echo off
setlocal
set "DS60_DOCKER_NO_PAUSE="
for %%A in (%*) do (
  if /I "%%~A"=="-NonInteractive" set "DS60_DOCKER_NO_PAUSE=1"
  if /I "%%~A"=="-DiagnosticsOnly" set "DS60_DOCKER_NO_PAUSE=1"
  if /I "%%~A"=="doctor" set "DS60_DOCKER_NO_PAUSE=1"
)
if not exist "%~dp0scripts\start_docker_windows.ps1" (
  echo Extract all files from the Windows Starter ZIP before running this file.
  if not defined DS60_DOCKER_NO_PAUSE pause
  exit /b 2
)
set "DS60_WINDOWS_PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe" set "DS60_WINDOWS_PS=%SystemRoot%\Sysnative\WindowsPowerShell\v1.0\powershell.exe"
"%DS60_WINDOWS_PS%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_docker_windows.ps1" %*
set "DS60_DOCKER_EXIT=%ERRORLEVEL%"
if "%DS60_DOCKER_EXIT%"=="3010" echo Restart Windows when convenient, then run this same starter again.
if not "%DS60_DOCKER_EXIT%"=="0" if not defined DS60_DOCKER_NO_PAUSE pause
exit /b %DS60_DOCKER_EXIT%
