@echo off
title Information Cascade Intelligence - Backend Server
cd /d "%~dp0backend"
set PYTHONPATH=.

echo ====================================================================
echo  INFORMATION CASCADE INTELLIGENCE - BACKEND SERVICE
echo  "We don't just detect information. We understand its journey."
echo ====================================================================

if not exist .venv\Scripts\python.exe (
    echo [1/2] Virtual environment not found. Initializing .venv...
    py -m venv .venv 2>nul || python -m venv .venv
    echo [2/2] Installing dependencies...
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

echo.
echo Starting FastAPI Uvicorn Server at http://127.0.0.1:8000 ...
echo API Documentation available at: http://127.0.0.1:8000/docs
echo Health Check: http://127.0.0.1:8000/api/health
echo.

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Backend server exited with code %ERRORLEVEL%.
    pause
)
