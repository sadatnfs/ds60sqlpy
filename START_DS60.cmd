@echo off
setlocal

rem Double-click this file for the guided Windows course startup.
rem The PowerShell orchestrator resolves the repository from its own location,
rem so paths containing spaces and launches from File Explorer are supported.
pushd "%~dp0" >nul
if errorlevel 1 (
    echo DS60 could not open the repository folder:
    echo   %~dp0
    pause
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass ^
    -File "%~dp0scripts\start_ds60.ps1" -PauseOnError %*
set "DS60_EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %DS60_EXIT_CODE%
