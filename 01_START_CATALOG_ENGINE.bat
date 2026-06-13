@echo off
chcp 65001 >nul
title BKS 01 - Catalog Engine

cd /d "%~dp0"

echo.
echo  BKS 01 - CATALOG ENGINE
echo  =======================
echo.

set "PYTHON_EXE="

echo [1/4] Cerco ambiente Python valido...

if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import flask,pandas,PIL,requests,numpy,werkzeug" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
        echo OK - uso .venv_catalog
    )
)

if not defined PYTHON_EXE if exist ".venv_dashboard\Scripts\python.exe" (
    ".venv_dashboard\Scripts\python.exe" -c "import flask,pandas,PIL,requests,numpy,werkzeug" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=.venv_dashboard\Scripts\python.exe"
        echo OK - uso .venv_dashboard
    )
)

if not defined PYTHON_EXE (
    echo Creo .venv_catalog...
    py -m venv .venv_catalog >nul 2>&1
    if %errorlevel% neq 0 (
        python -m venv .venv_catalog
    )
    if %errorlevel% neq 0 (
        echo ERRORE: impossibile creare .venv_catalog.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
)

echo.
echo [2/4] Verifico dipendenze...
"%PYTHON_EXE%" -c "import flask,pandas,PIL,requests,numpy,werkzeug" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installo dipendenze catalogo...
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PYTHON_EXE%" -m pip install flask pandas pillow requests numpy werkzeug scipy
    if %errorlevel% neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        echo Prova manualmente: %PYTHON_EXE% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo OK - dipendenze presenti
)

echo.
echo [3/4] Preparo cartelle...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "output\images" mkdir output\images
if not exist "temp" mkdir temp
echo OK - cartelle pronte

echo.
echo [4/4] Avvio server...
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
