@echo off
REM GenAI Chat Assistant with RAG - Quick Setup Script for Windows

echo ==================================
echo RAG Chat Assistant Setup
echo ==================================
echo.

REM Check Python
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo.
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

REM Create .env file
echo.
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env and add your ANTHROPIC_API_KEY
) else (
    echo .env file already exists
)

REM Success
echo.
echo ==================================
echo Setup Complete! ✓
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Edit .env and add your Claude API key:
echo    ANTHROPIC_API_KEY=sk_test_...
echo.
echo 2. Run the application:
echo    python -m main
echo.
echo 3. Open browser:
echo    http://localhost:8000
echo.
echo For deployment, see DEPLOYMENT.md
echo.
pause
