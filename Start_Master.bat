@echo off
chcp 65001 >nul
title BKS MASTER CONTROL PLANE

cd /d "%~dp0"

echo.
echo  BKS MASTER CONTROL PLANE
echo  ========================
echo.

py -c "import sys; print(sys.version)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python launcher py.exe non trovato.
    echo Installa Python 3.13+ e riprova.
    pause
    exit /b 1
)

if not exist ".venv_dashboard\Scripts\activate.bat" (
    echo [1/3] Creo ambiente .venv_dashboard...
    py -m venv .venv_dashboard
    if %errorlevel% neq 0 (
        echo ERRORE: impossibile creare .venv_dashboard.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente .venv_dashboard presente.
)

call .venv_dashboard\Scripts\activate.bat

echo [2/3] Verifico dipendenze master Streamlit...
python -c "import streamlit,pandas,requests,PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installo dipendenze da ecommerce_automation\requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r ecommerce_automation\requirements.txt
    if %errorlevel% neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        pause
        exit /b 1
    )
) else (
    echo Dipendenze presenti.
)

echo.
echo [3/3] Avvio nuova interfaccia master...
echo Apri: http://127.0.0.1:8600
echo.

start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8600"
python -m streamlit run streamlit_master.py --server.port 8600 --server.address 127.0.0.1

echo.
echo Master fermato.
pause
