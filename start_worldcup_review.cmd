@echo off
setlocal
set "WORLDCUP_PROJECT=%~dp0."
set "REVIEW_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%REVIEW_PYTHON%" (
    echo Set up the Python environment using README.md first.
    pause
    exit /b 1
)
"%REVIEW_PYTHON%" -B -m streamlit run "%~dp0worldcup_review_app.py" --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false --theme.base light
if errorlevel 1 pause
