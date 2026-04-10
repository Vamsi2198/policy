@echo off
REM START_DASHBOARD.bat - One-click launch for Governance Actions Dashboard
REM 
REM This script starts both:
REM   1. Flask API Server (port 5000)
REM   2. Streamlit Dashboard (port 8501)
REM
REM Simply double-click to start!

title Governance Actions Dashboard

cd /d "%~dp0"

echo.
echo ===============================================================================
echo  ^^! GOVERNANCE ACTIONS DASHBOARD
echo     Atlan Actions Engine - Complete Solution
echo     Starting Services...
echo.

set "PYTHON=C:\Users\HP\OneDrive\Documents\policy\s3_policy\.venv\Scripts\python.exe"

REM Check if Python exists
if not exist "%PYTHON%" (
    echo ERROR: Python not found at %PYTHON%
    echo.
    echo Please ensure the virtual environment is set up.
    pause
    exit /b 1
)

echo [1/2] Starting Flask API Server (port 5000)...
start "" "%PYTHON%" "atlan_api_server.py"
timeout /t 3 /nobreak

echo.
echo [2/2] Starting Streamlit Dashboard (port 8501)...
echo.
echo ===============================================================================
echo   ^* Opening: http://localhost:8501
echo   ^* API: http://localhost:5000
echo   ^* Press Ctrl+C to stop all services
echo ===============================================================================
echo.

REM Run Streamlit (this will block until closed)
"%PYTHON%" -m streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0

echo.
echo Governance Dashboard stopped.
echo.
pause
