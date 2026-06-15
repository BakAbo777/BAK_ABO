@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS MASTER CONTROL PLANE

cd /d "%~dp0"

:MENU
cls
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║          BKS MASTER CONTROL PLANE                   ║
echo  ║          BakAbo / BKS Studio — Workflow Hub         ║
echo  ╠══════════════════════════════════════════════════════╣
echo  ║                                                      ║
echo  ║  SEQUENZA OPERATIVA CORRETTA:                        ║
echo  ║                                                      ║
echo  ║  [1]  Catalog Engine        :5000  (PRIMA)          ║
echo  ║       Elabora CSV, arricchisce, esporta Shopify      ║
echo  ║                                                      ║
echo  ║  [2]  Collections Dashboard :8501                    ║
echo  ║       Console automazione collezioni Shopify         ║
echo  ║                                                      ║
echo  ║  [3]  Metafields Runner     :8502                    ║
echo  ║       Aggiunge metafields ai prodotti importati      ║
echo  ║                                                      ║
echo  ║  [4]  Image Factory         :8503                    ║
echo  ║       Genera e processa immagini prodotto            ║
echo  ║                                                      ║
echo  ║  [5]  Master Panel          :8600  (MONITORAGGIO)   ║
echo  ║       Hub centrale BKS con stato sistema             ║
echo  ║                                                      ║
echo  ║  [A]  AVVIA TUTTO in sequenza (finestre separate)    ║
echo  ║  [Q]  Esci                                           ║
echo  ║                                                      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
set /p SCELTA=  Scelta:

if /i "!SCELTA!"=="1" goto LAUNCH_01
if /i "!SCELTA!"=="2" goto LAUNCH_02
if /i "!SCELTA!"=="3" goto LAUNCH_03
if /i "!SCELTA!"=="4" goto LAUNCH_04
if /i "!SCELTA!"=="5" goto LAUNCH_MASTER
if /i "!SCELTA!"=="A" goto LAUNCH_ALL
if /i "!SCELTA!"=="Q" exit /b 0
goto MENU

:: ─────────────────────────────────────────────────
:LAUNCH_01
echo.
echo  Avvio [1] Catalog Engine su :5000 ...
start "BKS 01 - Catalog Engine" cmd /k "cd /d ""%~dp0"" && call 01_START_CATALOG_ENGINE.bat"
goto MENU

:LAUNCH_02
echo.
echo  Avvio [2] Collections Dashboard su :8501 ...
start "BKS 02 - Collections Dashboard" cmd /k "cd /d ""%~dp0"" && call 02_START_COLLECTIONS_DASHBOARD.bat"
goto MENU

:LAUNCH_03
echo.
echo  Avvio [3] Metafields Runner su :8502 ...
start "BKS 03 - Metafields Runner" cmd /k "cd /d ""%~dp0"" && call 03_START_METAFIELDS_RUNNER.bat"
goto MENU

:LAUNCH_04
echo.
echo  Avvio [4] Image Factory su :8503 ...
start "BKS 04 - Image Factory" cmd /k "cd /d ""%~dp0"" && call 04_START_IMAGE_FACTORY.bat"
goto MENU

:LAUNCH_MASTER
echo.
echo  Avvio [5] Master Panel su :8600 ...
goto START_MASTER_INLINE

:: ─────────────────────────────────────────────────
:LAUNCH_ALL
cls
echo.
echo  Avvio sequenza completa BKS...
echo.

echo  [1/5] Catalog Engine :5000...
start "BKS 01 - Catalog Engine" cmd /k "cd /d ""%~dp0"" && call 01_START_CATALOG_ENGINE.bat"
timeout /t 4 /nobreak >nul

echo  [2/5] Collections Dashboard :8501...
start "BKS 02 - Collections Dashboard" cmd /k "cd /d ""%~dp0"" && call 02_START_COLLECTIONS_DASHBOARD.bat"
timeout /t 3 /nobreak >nul

echo  [3/5] Metafields Runner :8502...
start "BKS 03 - Metafields Runner" cmd /k "cd /d ""%~dp0"" && call 03_START_METAFIELDS_RUNNER.bat"
timeout /t 3 /nobreak >nul

echo  [4/5] Image Factory :8503...
start "BKS 04 - Image Factory" cmd /k "cd /d ""%~dp0"" && call 04_START_IMAGE_FACTORY.bat"
timeout /t 3 /nobreak >nul

echo  [5/5] Master Panel :8600 (questa finestra)...
echo.
echo  Tutti i pannelli avviati. Apri i browser:
echo    Catalog Engine        :  http://localhost:5000
echo    Collections Dashboard :  http://localhost:8501
echo    Metafields Runner     :  http://localhost:8502
echo    Image Factory         :  http://localhost:8503
echo    Master Panel          :  http://127.0.0.1:8600
echo.
timeout /t 2 /nobreak >nul
goto START_MASTER_INLINE

:: ─────────────────────────────────────────────────
:START_MASTER_INLINE
py -c "import sys; print(sys.version)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python launcher py.exe non trovato.
    pause
    exit /b 1
)

if not exist ".venv_dashboard\Scripts\activate.bat" (
    echo Creo .venv_dashboard...
    py -m venv .venv_dashboard
)

call .venv_dashboard\Scripts\activate.bat

python -c "import streamlit,pandas,requests,PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installo dipendenze master...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r ecommerce_automation\requirements.txt
)

echo.
echo  Master Panel avviato su http://127.0.0.1:8600
echo  Premi CTRL+C per fermare.
echo.
start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8600"
python -m streamlit run streamlit_master.py --server.port 8600 --server.address 127.0.0.1

echo.
echo Master fermato.
pause
