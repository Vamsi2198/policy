@echo off
echo Checking for OpenAI API Key...
if "%OPENAI_API_KEY%"=="" (
    echo ❌ OPENAI_API_KEY environment variable not set!
    echo Please set the OPENAI_API_KEY environment variable first.
    echo Example: set OPENAI_API_KEY=your_key_here
    pause
    exit /b 1
) else (
    echo ✅ OpenAI API Key found in environment!
    echo Key preview: %OPENAI_API_KEY:~0,20%...
)
python ai_control_plane.py