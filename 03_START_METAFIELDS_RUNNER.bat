@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS 03 - Metafields Runner

cd /d "%~dp0"

echo.
echo  BKS 03 - METAFIELDS RUNNER  [STEP 3 di 5]
echo  ============================================
echo.
echo  Dipende da: prodotti gia' importati su Shopify via 01
echo.

py -c "import sys; print(sys.version)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python launcher py.exe non trovato.
    echo Installa Python 3.10+ e riprova.
    pause
    exit /b 1
)

if not exist "streamlit_metafields_runner.py" (
    echo ERRORE: streamlit_metafields_runner.py non trovato in %CD%
    pause
    exit /b 1
)

if not exist ".venv_metafields\Scripts\activate.bat" (
    echo [1/3] Creo ambiente .venv_metafields...
    py -m venv .venv_metafields
    if !errorlevel! neq 0 (
        echo ERRORE: impossibile creare .venv_metafields.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente .venv_metafields presente.
)

call .venv_metafields\Scripts\activate.bat

echo [2/3] Verifico dipendenze...
python -c "import streamlit, pandas, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installo dipendenze minime...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install streamlit pandas requests
    if !errorlevel! neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        pause
        exit /b 1
    )
) else (
    echo Dipendenze presenti.
)

echo.
echo [3/3] Avvio interfaccia...
echo Apri: http://localhost:8502
echo.

start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8502"
streamlit run streamlit_metafields_runner.py --server.port 8502

pause
