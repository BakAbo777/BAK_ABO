@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================================
echo  BKS STUDIO — BAKABO IMAGE FACTORY v1.1
echo =====================================================
echo.

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 ( echo ERROR: Python not found. Install Python 3.10+. && pause && exit )
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

:: Create desktop shortcut on first run
if not exist "venv\.shortcut_done" (
    python create_shortcut.py
    echo. > "venv\.shortcut_done"
)

echo.
echo Starting dashboard at http://localhost:8503
echo.
streamlit run app.py --server.port 8503 --browser.gatherUsageStats false

pause
