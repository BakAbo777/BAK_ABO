@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS MASTER CONTROL PLANE v4.0 — BakAbo

cd /d "%~dp0"

:: ═══════════════════════════════════════════════════════════════════════════
:: ANSI colors — Windows 10+ VT100
:: ═══════════════════════════════════════════════════════════════════════════
for /f "delims=" %%E in ('powershell -NoProfile -Command "[char]0x1b"') do set "ESC=%%E"
set "GRN=%ESC%[92m"
set "RED=%ESC%[91m"
set "YEL=%ESC%[93m"
set "CYA=%ESC%[96m"
set "WHT=%ESC%[97m"
set "DIM=%ESC%[90m"
set "RST=%ESC%[0m"
set "ROOT=%~dp0"

goto :STARTUP

:: ═══════════════════════════════════════════════════════════════════════════
:CHECK_PORT
set "PSTAT=OFFLINE"
netstat -ano 2>nul | findstr /R ":%1[^0-9]" | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 set "PSTAT=ONLINE"
goto :eof

:KILL_PORT
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %1 -State Listen -EA SilentlyContinue | ForEach-Object { $p=$_.OwningProcess; Stop-Process -Id $p -Force -EA SilentlyContinue; Write-Host ('    Kill PID '+$p+' porta %1') }" 2>nul
goto :eof

:KILL_AND_WAIT
call :KILL_PORT %1
timeout /t 2 /nobreak >nul
goto :eof

:: ═══════════════════════════════════════════════════════════════════════════
:STARTUP
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  %RED%[ERRORE] Python py.exe non trovato.%RST%
    pause
    exit /b 1
)
set "NO_ENV="
if not exist ".env" set "NO_ENV=1"

:: ═══════════════════════════════════════════════════════════════════════════
:MENU
cls

call :CHECK_PORT 8501
set "S1=!PSTAT!"
call :CHECK_PORT 8010
set "S2=!PSTAT!"
call :CHECK_PORT 8600
set "S3=!PSTAT!"

set /a NONL=0
if "!S1!"=="ONLINE" set /a NONL+=1
if "!S2!"=="ONLINE" set /a NONL+=1
if "!S3!"=="ONLINE" set /a NONL+=1

set "D1=%RED%OFFLINE%RST%"
if "!S1!"=="ONLINE" set "D1=%GRN%ONLINE %RST%"
set "D2=%RED%OFFLINE%RST%"
if "!S2!"=="ONLINE" set "D2=%GRN%ONLINE %RST%"
set "D3=%RED%OFFLINE%RST%"
if "!S3!"=="ONLINE" set "D3=%GRN%ONLINE %RST%"

echo.
echo  %CYA%╔══════════════════════════════════════════════════════════╗%RST%
echo  %CYA%║%WHT%        BKS MASTER CONTROL PLANE  v4.0                 %CYA%║%RST%
echo  %CYA%║%DIM%        BakAbo / BKS Studio — bakabo.club               %CYA%║%RST%
echo  %CYA%╚══════════════════════════════════════════════════════════╝%RST%
echo.
echo  %WHT%STATO SERVIZI%RST% — %DIM%!NONL!/3 online%RST%
echo  %DIM%──────────────────────────────────────────────────────────%RST%
echo  [!D1!]  %WHT%[1]%RST%  BKS Studio (Streamlit)  :8501
echo  [!D2!]  %WHT%[2]%RST%  %CYA%Try-On AI Engine%RST%        :8010
echo  [!D3!]  %WHT%[3]%RST%  Master Panel             :8600   %DIM%tablet: 192.168.1.103%RST%
echo  %DIM%──────────────────────────────────────────────────────────%RST%
if defined NO_ENV echo  %YEL%  [!] .env non trovato — credenziali API mancanti%RST%
echo.
echo  %WHT%AVVIO:%RST%  [1-3] singolo  ^|  [A] tutto  ^|  [K] kill porte  ^|  [Q] esci
echo  %WHT%TOOLS:%RST%  [B] browser  ^|  [S] refresh
echo.
set /p SCELTA=  Scelta:

if /i "!SCELTA!"=="1" goto LAUNCH_01
if /i "!SCELTA!"=="2" goto LAUNCH_02
if /i "!SCELTA!"=="3" goto LAUNCH_MASTER
if /i "!SCELTA!"=="A" goto LAUNCH_ALL
if /i "!SCELTA!"=="B" goto OPEN_BROWSERS
if /i "!SCELTA!"=="S" goto MENU
if /i "!SCELTA!"=="K" goto KILL_ALL
if /i "!SCELTA!"=="Q" exit /b 0
goto MENU

:: ═══════════════════════════════════════════════════════════════════════════
:LAUNCH_01
echo.
echo  %GRN%Avvio [1] Streamlit :8501 ...%RST%
if "!S1!"=="ONLINE" (
    echo  %YEL%  Porta 8501 occupata. Kill automatico...%RST%
    call :KILL_AND_WAIT 8501
)
start "BKS 01 - Streamlit" /d "%ROOT%" cmd /k 01_START_CATALOG_ENGINE.bat
timeout /t 1 /nobreak >nul
goto MENU

:LAUNCH_02
echo.
echo  %GRN%Avvio [2] Try-On Engine :8010 ...%RST%
if "!S2!"=="ONLINE" (
    echo  %YEL%  Porta 8010 occupata. Kill automatico...%RST%
    call :KILL_AND_WAIT 8010
)
start "BKS 02 - TryOn Engine" /d "%ROOT%" cmd /k 05_START_TRYON_ENGINE.bat
timeout /t 1 /nobreak >nul
goto MENU

:: ═══════════════════════════════════════════════════════════════════════════
:OPEN_BROWSERS
cls
echo.
echo  %CYA%Apertura browser per i servizi online...%RST%
echo.
set /a _OPN=0
if "!S1!"=="ONLINE" (
    start http://localhost:8501
    set /a _OPN+=1
    echo  %GRN%->%RST%  http://localhost:8501      [BKS Studio]
)
if "!S2!"=="ONLINE" (
    start http://127.0.0.1:8010/health
    set /a _OPN+=1
    echo  %GRN%->%RST%  http://127.0.0.1:8010      [Try-On Engine]
)
if "!S3!"=="ONLINE" (
    start http://127.0.0.1:8600
    set /a _OPN+=1
    echo  %GRN%->%RST%  http://127.0.0.1:8600      [Master Panel]
)
if !_OPN! equ 0 (
    echo  %YEL%Nessun servizio online. Avvia con [1-3] o [A].%RST%
)
echo.
timeout /t 2 /nobreak >nul
goto MENU

:: ═══════════════════════════════════════════════════════════════════════════
:KILL_ALL
cls
echo.
echo  %YEL%Kill processi BKS sulle porte 8010 8501 8600...%RST%
echo.
call :KILL_PORT 8010
call :KILL_PORT 8501
call :KILL_PORT 8600
echo.
echo  %GRN%Completato.%RST%
timeout /t 2 /nobreak >nul
goto MENU

:: ═══════════════════════════════════════════════════════════════════════════
:LAUNCH_ALL
cls
echo.
echo  %CYA%Avvio completo BKS...%RST%
echo.

:: Kill preventivo su tutte le porte
echo  %DIM%Kill porte esistenti...%RST%
call :KILL_PORT 8501
call :KILL_PORT 8010
call :KILL_PORT 8600
timeout /t 2 /nobreak >nul

echo  %DIM%[1/3]%RST% Streamlit :8501...
start "BKS 01 - Streamlit" /d "%ROOT%" cmd /k 01_START_CATALOG_ENGINE.bat
timeout /t 5 /nobreak >nul

echo  %DIM%[2/3]%RST% Try-On Engine :8010...
start "BKS 02 - TryOn Engine" /d "%ROOT%" cmd /k 05_START_TRYON_ENGINE.bat
timeout /t 3 /nobreak >nul

echo  %DIM%[3/3]%RST% Master Panel :8600 (questa finestra)...
echo.
goto START_MASTER_INLINE

:: ═══════════════════════════════════════════════════════════════════════════
:LAUNCH_MASTER
echo.
echo  %GRN%Avvio [3] Master Panel :8600 ...%RST%
if "!S3!"=="ONLINE" (
    echo  %YEL%  Porta 8600 occupata. Kill automatico...%RST%
    call :KILL_AND_WAIT 8600
)

:: ═══════════════════════════════════════════════════════════════════════════
:START_MASTER_INLINE
if not exist ".venv_dashboard\Scripts\activate.bat" (
    echo  %YEL%Creo .venv_dashboard...%RST%
    py -m venv .venv_dashboard
    if !errorlevel! neq 0 (
        echo  %RED%ERRORE: impossibile creare .venv_dashboard.%RST%
        pause
        exit /b 1
    )
)

call .venv_dashboard\Scripts\activate.bat

python -c "import streamlit,pandas,requests,PIL" >nul 2>&1
if !errorlevel! neq 0 (
    echo  %YEL%Installo dipendenze master...%RST%
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo  %RED%ERRORE: installazione dipendenze fallita.%RST%
        pause
        exit /b 1
    )
)

echo.
echo  %CYA%╔════════════════════════════════════════════════╗%RST%
echo  %CYA%║%WHT%  BKS Master Panel — porta 8600               %CYA%║%RST%
echo  %CYA%║%DIM%  Local:   http://127.0.0.1:8600              %CYA%║%RST%
echo  %CYA%║%DIM%  Tablet:  http://192.168.1.103:8600          %CYA%║%RST%
echo  %CYA%║%DIM%  CTRL+C per fermare                          %CYA%║%RST%
echo  %CYA%╚════════════════════════════════════════════════╝%RST%
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8600"
python -m streamlit run streamlit_master.py --server.port 8600 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false

echo.
echo  %DIM%Master fermato.%RST%
pause
