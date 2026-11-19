@echo off
setlocal
"%~dp0python\python.exe" -I -m sentiment_app.cli %*
exit /b %ERRORLEVEL%
