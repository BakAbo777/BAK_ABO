@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS 01 - Catalog Engine

cd /d "%~dp0"

echo.
echo  BKS 01 - CATALOG ENGINE  [STEP 1 di 5 — avviare PRIMO]
echo  ========================================================
echo.
echo  Sequenza: 01:5000 → 02:8501 → 03:8502 → 04:8503 → Master:8600
echo.

set "PYTHON_EXE="

echo [1/5] Cerco ambiente Python valido...

if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import flask,pandas,PIL,requests,numpy,werkzeug,scipy,dotenv" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
        echo OK - uso .venv_catalog
    )
)

if not defined PYTHON_EXE if exist ".venv_dashboard\Scripts\python.exe" (
    ".venv_dashboard\Scripts\python.exe" -c "import flask,pandas,PIL,requests,numpy,werkzeug,scipy,dotenv" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=.venv_dashboard\Scripts\python.exe"
        echo OK - uso .venv_dashboard
    )
)

if not defined PYTHON_EXE (
    echo Creo .venv_catalog...
    py -m venv .venv_catalog >nul 2>&1
    if !errorlevel! neq 0 (
        python -m venv .venv_catalog
    )
    if !errorlevel! neq 0 (
        echo ERRORE: impossibile creare .venv_catalog.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
)

echo.
echo [2/5] Verifico dipendenze...
"%PYTHON_EXE%" -c "import flask,pandas,PIL,requests,numpy,werkzeug,scipy,dotenv" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installo dipendenze da requirements.txt...
    "%PYTHON_EXE%" -m pip install --upgrade pip >nul 2>&1
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        pause
        exit /b 1
    )
) else (
    echo OK - dipendenze presenti
)

echo.
echo [3/5] Preparo cartelle...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "output\images" mkdir output\images
if not exist "temp" mkdir temp
if not exist "archivio" mkdir archivio
if not exist "collezioni_csv" mkdir collezioni_csv
echo OK - cartelle pronte

echo.
echo [4/5] Caricamento automatico catalogo CSV...
"%PYTHON_EXE%" _init_catalog.py
if !errorlevel! neq 0 (
    echo.
    echo ATTENZIONE: Nessun CSV trovato. Metti un file CSV in una di queste cartelle:
    echo   - archivio\
    echo   - collezioni_csv\
    echo   - input\
    echo Puoi anche caricare manualmente dall'interfaccia web.
    echo.
)

echo.
echo [5/5] Avvio server...

if not exist "catalog_engine.py" (
    echo ERRORE: catalog_engine.py non trovato in %CD%
    pause
    exit /b 1
)

echo.
echo Apri: http://localhost:5000
echo Premi CTRL+C per fermare il server.
echo.

set "BKS_FLASK_DEBUG=0"
start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"
"%PYTHON_EXE%" catalog_engine.py

echo.
echo Server fermato.
pause