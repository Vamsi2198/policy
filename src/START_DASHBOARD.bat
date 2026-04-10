@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ===============================================================================
echo  ^^! GOVERNANCE ACTIONS DASHBOARD
echo     Starting Atlan Actions Engine...
echo.

REM Use the virtual environment Python
set "PYTHON=C:\Users\HP\OneDrive\Documents\policy\s3_policy\.venv\Scripts\python.exe"
echo Using Virtual Environment: %PYTHON%

echo.
echo [1/2] Starting Flask API Server...
start "" "%PYTHON%" "atlan_api_server.py"
timeout /t 2 /nobreak

echo.
echo [2/2] Starting Streamlit Dashboard...
echo.
echo ===============================================================================
echo   ^* Local: http://localhost:8501
echo   ^* Network: http://192.168.31.243:8501
echo   ^* Share this URL with friends: http://192.168.31.243:8501
echo ===============================================================================
echo.
"%PYTHON%" -m streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0

echo.
echo Governance Dashboard stopped.
pause
