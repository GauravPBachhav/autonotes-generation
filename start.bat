@echo off
REM Autonotes Generation - Start Script (Windows)

echo.
echo.
echo 🎓 Autonotes Generation - Quick Start
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

echo ✅ Python version:
python --version
echo ✅ Node.js version:
node --version
echo.

REM Start Backend
echo 🚀 Starting Backend Server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo    Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    Installing Python dependencies...
    pip install -r requirements.txt
)

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp
if not exist "output" mkdir output
if not exist "logs" mkdir logs

REM Start backend in new window
start "Autonotes Backend" cmd /k python main.py
echo    Backend started
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start Frontend
echo 🚀 Starting Frontend Server...
cd ..\frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo    Installing Node dependencies...
    call npm install
)

REM Start frontend in new window
start "Autonotes Frontend" cmd /k npm run dev
echo    Frontend started
echo    App: http://localhost:5173
echo.

echo ======================================
echo ✨ All services started successfully!
echo.
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo Docs:     http://localhost:8000/docs
echo.
echo Close the terminal windows to stop services
echo ======================================
echo.
pause
