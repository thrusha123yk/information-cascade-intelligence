@echo off
title Information Cascade Intelligence - Frontend Dashboard
cd /d "%~dp0frontend"

echo ====================================================================
echo  INFORMATION CASCADE INTELLIGENCE - REACT DASHBOARD
echo ====================================================================

if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)

echo.
echo Starting Vite Dev Server at http://localhost:5173 ...
echo.
npm run dev
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Frontend server exited with code %ERRORLEVEL%.
    pause
)
