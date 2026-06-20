@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title BKS 01 - Catalog Engine (Streamlit :8501)

cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONDONTWRITEBYTECODE=1"

echo.
echo  BKS 01 - CATALOG ENGINE  [Streamlit - porta 8501]
echo  ===================================================
echo.

:: -- [0/5] Check porta 8501 ---------------------------------------------------
echo [0/5] Verifico porta 8501...
netstat -ano | findstr ":8501 " >nul 2>&1
if !errorlevel! equ 0 (
    echo.
    echo  ATTENZIONE: porta 8501 gia in uso.
    choice /C SKC /M "  [S] Continua   [K] Killa processo   [C] Esci"
    if !errorlevel! equ 3 exit /b 0
    if !errorlevel! equ 2 (
        echo  Termino processo su 8501...
        powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8501 -State Listen -EA SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -EA SilentlyContinue; Write-Host ('    Kill PID '+$_.OwningProcess) }" 2>nul
        timeout /t 1 /nobreak >nul
    )
    echo.
) else (
    echo OK - porta 8501 libera
)

:: -- [1/5] Python env ---------------------------------------------------------
set "PYTHON_EXE="
echo.
echo [1/5] Cerco ambiente Python valido...

if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import streamlit,pandas,PIL,requests,dotenv" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
        echo OK - uso .venv_catalog
        goto :deps_ok
    ) else (
        echo .venv_catalog trovato ma dipendenze mancanti
    )
)

if not defined PYTHON_EXE (
    if exist ".venv_dashboard\Scripts\python.exe" (
        ".venv_dashboard\Scripts\python.exe" -c "import streamlit,pandas,PIL,requests,dotenv" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=.venv_dashboard\Scripts\python.exe"
            echo OK - uso .venv_dashboard
            goto :deps_ok
        )
    )
)

if not defined PYTHON_EXE (
    echo Creo .venv_catalog...
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        py -m venv .venv_catalog
    ) else (
        python -m venv .venv_catalog
    )
    set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
)

:: -- [2/5] Dipendenze ---------------------------------------------------------
echo.
echo [2/5] Verifico dipendenze...
"%PYTHON_EXE%" -c "import streamlit,pandas,PIL,requests,dotenv" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installo da requirements.txt...
    "%PYTHON_EXE%" -m pip install --upgrade pip --quiet
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    echo OK - dipendenze installate
) else (
    echo OK - dipendenze presenti
)

:deps_ok

:: -- [3/5] Cartelle -----------------------------------------------------------
echo.
echo [3/5] Preparo cartelle...
for %%D in (input output output\images temp archivio collezioni_csv logs) do (
    if not exist "%%D" mkdir "%%D" >nul 2>&1
)
echo OK - cartelle pronte

:: -- [4/5] Catalogo CSV -------------------------------------------------------
echo.
echo [4/5] Caricamento automatico catalogo CSV...
if exist "_init_catalog.py" (
    "%PYTHON_EXE%" _init_catalog.py
    set "INIT_ERR=!errorlevel!"
    if !INIT_ERR! equ 0 (
        echo OK - catalogo caricato
    ) else if !INIT_ERR! equ 2 (
        echo  Nessun CSV trovato. Carica dalla pagina Catalogo in Streamlit.
    ) else (
        echo ATTENZIONE: _init_catalog.py errore !INIT_ERR!
    )
) else (
    echo SKIP - _init_catalog.py non trovato
)

:: -- [5/5] Avvio Streamlit ----------------------------------------------------
:start_server
echo.
echo [5/5] Avvio Streamlit...

if not exist "streamlit_master.py" (
    echo ERRORE: streamlit_master.py non trovato
    pause
    exit /b 1
)

echo %date% %time% - BKS Streamlit avviato >> logs\startup.log 2>nul

echo.
echo  +---------------------------------------------------+
echo  ^|  BKS Studio  -  Streamlit :8501                  ^|
echo  ^|  URL: http://localhost:8501                       ^|
echo  ^|  Premi CTRL+C per fermare                        ^|
echo  +---------------------------------------------------+
echo.

start "" cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8501"

"%PYTHON_EXE%" -m streamlit run streamlit_master.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

set "ST_EXIT=!errorlevel!"
echo %date% %time% - BKS Streamlit fermato exit=!ST_EXIT! >> logs\startup.log 2>nul

if !ST_EXIT! neq 0 (
    echo.
    echo  ERRORE exit=!ST_EXIT! - riprova manualmente:
    echo    !PYTHON_EXE! -m streamlit run streamlit_master.py
    echo.
)
pause
