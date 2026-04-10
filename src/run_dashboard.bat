@echo off
REM Governance Actions Dashboard - Windows Launcher
REM This script starts the complete Governance Actions Dashboard
REM (Flask API + Streamlit Frontend)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║   ⚡ GOVERNANCE ACTIONS DASHBOARD                         ║
echo ║      Launching Application...                             ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python installation found
python --version
echo.

REM Check if we're in the right directory
if not exist "atlan_api_server.py" (
    echo [ERROR] atlan_api_server.py not found
    echo.
    echo Please run this script from the src\ directory
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting Governance Actions Dashboard...
echo.

REM Run the startup script
python run_governance_dashboard.py

echo.
echo [INFO] Dashboard stopped
pause
