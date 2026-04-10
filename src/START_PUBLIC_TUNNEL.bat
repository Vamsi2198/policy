@echo off
REM START_PUBLIC_TUNNEL.bat - Open public URLs for Flask (5000) & Streamlit (8501)
cd /d "%~dp0"
set "PYTHON=C:\Users\HP\OneDrive\Documents\policy\s3_policy\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
  echo [ERROR] Virtual env python not found: %PYTHON%
  echo Please start your dashboard first, then re-run this.
  pause
  exit /b 1
)

"%PYTHON%" start_ngrok.py
