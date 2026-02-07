@echo off
REM Tax Helper - Run Script for Windows

echo 💷 Starting Tax Helper...
echo.
cd /d "%~dp0\.."
python -m streamlit run app.py
