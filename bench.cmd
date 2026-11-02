@echo off
rem Launcher for Windows: bench <command> [options]
setlocal
set "DIR=%~dp0"
set "PYTHONPATH=%DIR%src;%PYTHONPATH%"
where py >nul 2>nul && (py -3 -m benchlm %*) || (python -m benchlm %*)
endlocal
