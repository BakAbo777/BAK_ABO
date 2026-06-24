@echo off
cd /d "I:\BAK ABO"

:: Trova Python con Streamlit
set "PYTHON_EXE="
if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
)
if not defined PYTHON_EXE (
    if exist ".venv_dashboard\Scripts\python.exe" (
        ".venv_dashboard\Scripts\python.exe" -c "import streamlit" >nul 2>&1
        if !errorlevel! equ 0 set "PYTHON_EXE=.venv_dashboard\Scripts\python.exe"
    )
)
if not defined PYTHON_EXE (
    echo ERRORE: Python/Streamlit non trovato >> "I:\BAK ABO\logs\service.log"
    exit /b 1
)

:: Avvia Streamlit in background, log su file
start /B "" "%PYTHON_EXE%" -m streamlit run streamlit_master.py ^
    --server.port 8501 ^
    --server.headless true ^
    --server.address 0.0.0.0 ^
    --browser.gatherUsageStats false ^
    >> "I:\BAK ABO\logs\streamlit_service.log" 2>&1
