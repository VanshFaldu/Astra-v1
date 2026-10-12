@echo off
cd /d "%~dp0"
py --version >nul 2>&1
if not errorlevel 1 (
    py server.py
) else if exist "%LocalAppData%\Programs\Python\Python314\python.exe" (
    "%LocalAppData%\Programs\Python\Python314\python.exe" server.py
) else (
    python server.py
)
pause
