@echo off
REM Tax Helper - Installation Script for Windows

echo 💷 Tax Helper - Installation
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To run Tax Helper:
echo    Double-click RUN.bat
echo.
echo    OR
echo.
echo    python -m streamlit run app.py
echo.
pause
