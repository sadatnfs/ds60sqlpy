@echo off
rem Guided setup and the coding-pad application. Paths with spaces are supported.
call "%~dp0START_DS60.cmd" -LearningLab %*
exit /b %ERRORLEVEL%
