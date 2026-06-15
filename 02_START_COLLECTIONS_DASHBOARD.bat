@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS 02 - Automation Console

cd /d "%~dp0"

echo.
echo  BKS 02 - COLLECTIONS DASHBOARD  [STEP 2 di 5]
echo  ================================================
echo.
echo  Dipende da: 01 Catalog Engine :5000
echo.

py -c "import sys; print(sys.version)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python launcher py.exe non trovato.
    echo Installa Python 3.13+ e riprova.
    pause
    exit /b 1
)

if not exist "streamlit_collections.py" (
    echo ERRORE: streamlit_collections.py non trovato in %CD%
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERRORE: requirements.txt non trovato in %CD%
    pause
    exit /b 1
)

if not exist ".venv_dashboard\Scripts\activate.bat" (
    echo [1/3] Creo ambiente .venv_dashboard...
    py -m venv .venv_dashboard
    if !errorlevel! neq 0 (
        echo ERRORE: impossibile creare .venv_dashboard.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente .venv_dashboard presente.
)

call .venv_dashboard\Scripts\activate.bat

echo [2/3] Verifico dipendenze...
python -c "import streamlit, pandas, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installo dipendenze da requirements.txt...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        pause
        exit /b 1
    )
) else (
    echo Dipendenze presenti.
)

echo.
echo [3/3] Avvio cruscotto...
echo Apri: http://localhost:8501
echo.

start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8501"
streamlit run streamlit_collections.py --server.port 8501

pause
