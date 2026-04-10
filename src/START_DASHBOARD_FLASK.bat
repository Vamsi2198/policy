@echo off
REM START_DASHBOARD.bat - Governance Actions Dashboard Launcher

title Governance Actions Dashboard

cd /d "%~dp0"

echo.
echo ===============================================================================
echo  ^^! GOVERNANCE ACTIONS DASHBOARD
echo     Atlan Actions Engine
echo.

REM Use the virtual environment Python
set "PYTHON=C:\Users\HP\OneDrive\Documents\policy\s3_policy\.venv\Scripts\python.exe"
echo Using Virtual Environment: %PYTHON%

echo.
echo ===============================================================================
echo   ^* Local: http://localhost:5000
echo   ^* Network: http://192.168.31.243:5000
echo   ^* Share this URL with friends: http://192.168.31.243:5000
echo ===============================================================================
echo.

"%PYTHON%" "atlan_api_server.py"

echo.
echo Governance Dashboard stopped.
pause
