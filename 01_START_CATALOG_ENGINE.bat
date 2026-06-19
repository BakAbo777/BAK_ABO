
@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title BKS 01 - Catalog Engine (Streamlit)

cd /d "%~dp0"

:: -- Encoding UTF-8 obbligatorio per CSV BKS
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONDONTWRITEBYTECODE=1"

echo.
echo  BKS 01 - CATALOG ENGINE  [Streamlit - porta 8501]
echo  ===================================================
echo.

:: -- [0/5] Check porta 8501 libera ------------------------------------------
echo [0/5] Verifico porta 8501...
netstat -ano | findstr ":8501 " >nul 2>&1
if !errorlevel! equ 0 (
    echo.
    echo  ATTENZIONE: porta 8501 gia in uso.
    echo  Streamlit potrebbe essere gia avviato.
    echo.
    choice /C SC /M "  [S] Continua comunque   [C] Esci"
    if !errorlevel! equ 2 exit /b 0
    echo.
) else (
    echo OK - porta 8501 libera
)

:: -- [1/5] Ricerca ambiente Python valido ------------------------------------
set "PYTHON_EXE="

echo.
echo [1/5] Cerco ambiente Python valido...

:: Prova .venv_catalog
if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import streamlit,pandas,PIL,requests,dotenv" >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
        echo OK - uso .venv_catalog
        goto :deps_ok
    ) else (
        echo .venv_catalog trovato ma dipendenze mancanti - riinstallo
    )
)

:: Prova .venv_dashboard
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

:: Nessun venv valido - crea .venv_catalog
if not defined PYTHON_EXE (
    echo Creo .venv_catalog...
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        py -m venv .venv_catalog
    ) else (
        python --version >nul 2>&1
        if !errorlevel! equ 0 (
            python -m venv .venv_catalog
        ) else (
            echo.
            echo ERRORE: Python non trovato nel sistema.
            echo Installa Python 3.10+ da https://www.python.org/downloads/
            echo.
            pause
            exit /b 1
        )
    )
    if !errorlevel! neq 0 (
        echo ERRORE: impossibile creare .venv_catalog.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=.venv_catalog\Scripts\python.exe"
    echo OK - .venv_catalog creato
)

:: -- [2/5] Dipendenze --------------------------------------------------------
echo.
echo [2/5] Verifico dipendenze...

"%PYTHON_EXE%" -c "import streamlit,pandas,PIL,requests,dotenv" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installo dipendenze da requirements.txt...
    if not exist "requirements.txt" (
        echo ERRORE: requirements.txt non trovato
        pause
        exit /b 1
    )
    "%PYTHON_EXE%" -m pip install --upgrade pip --quiet
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo ERRORE: installazione fallita.
        pause
        exit /b 1
    )
    echo OK - dipendenze installate
) else (
    echo OK - dipendenze presenti
)

:deps_ok

:: -- [3/5] Cartelle ----------------------------------------------------------
echo.
echo [3/5] Preparo cartelle...
for %%D in (input output output\images temp archivio collezioni_csv logs) do (
    if not exist "%%D" (
        mkdir "%%D" >nul 2>&1
        echo   + %%D
    )
)
echo OK - cartelle pronte

:: -- [4/5] Caricamento catalogo CSV ------------------------------------------
echo.
echo [4/5] Caricamento automatico catalogo CSV...

if not exist "_init_catalog.py" (
    echo ATTENZIONE: _init_catalog.py non trovato - salto
    goto :start_server
)

"%PYTHON_EXE%" _init_catalog.py
set "INIT_ERR=!errorlevel!"

if !INIT_ERR! equ 0 (
    echo OK - catalogo caricato
) else if !INIT_ERR! equ 2 (
    echo.
    echo  Nessun CSV trovato automaticamente.
    echo  Carica il CSV dalla pagina Catalogo nell'app Streamlit.
    echo.
) else (
    echo ATTENZIONE: _init_catalog.py errore !INIT_ERR! - controlla logs\_init_catalog.log
)

:: -- [5/5] Avvio Streamlit ---------------------------------------------------
:start_server
echo.
echo [5/5] Avvio Streamlit...

if not exist "streamlit_master.py" (
    echo ERRORE: streamlit_master.py non trovato in %CD%
    pause
    exit /b 1
)

echo %date% %time% - BKS Streamlit avviato >> logs\startup.log

echo.
echo  +---------------------------------------------------+
echo  |  BKS Studio  -  Streamlit avviato                |
echo  |  URL: http://localhost:8501                       |
echo  |  Pagine: Master  Catalogo  Image Factory          |
echo  |  Premi CTRL+C per fermare                        |
echo  +---------------------------------------------------+
echo.

:: Apri browser dopo 5 secondi (Streamlit ha bisogno di un po' di piu)
start "" cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8501"

:: Avvia Streamlit - BLOCKING
"%PYTHON_EXE%" -m streamlit run streamlit_master.py ^
    --server.port 8501 ^
    --server.headless false ^
    --browser.gatherUsageStats false ^
    --server.fileWatcherType none

set "ST_EXIT=!errorlevel!"

echo.
echo %date% %time% - BKS Streamlit fermato (exit !ST_EXIT!) >> logs\startup.log

if !ST_EXIT! equ 0 (
    echo  Streamlit fermato normalmente.
) else (
    echo.
    echo  ERRORE: Streamlit si e fermato con codice !ST_EXIT!
    echo  Suggerimento: esegui manualmente:
    echo    .venv_catalog\Scripts\python.exe -m streamlit run streamlit_master.py
    echo  per vedere l errore direttamente.
    echo.
)
echo.
pause
