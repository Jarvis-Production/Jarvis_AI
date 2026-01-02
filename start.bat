@echo off
REM Jarvis AI - Start Script for Windows

echo ===================================
echo     Jarvis AI - Starting...
echo ===================================

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env file with your API keys
    echo Then run this script again
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)

echo.
echo Starting Backend...
start "Jarvis Backend" cmd /k python -m backend.main

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend...
cd frontend
start "Jarvis Frontend" cmd /k npm run dev

echo.
echo ===================================
echo    Jarvis AI is running!
echo ===================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close the terminal windows to stop services
echo.
pause
