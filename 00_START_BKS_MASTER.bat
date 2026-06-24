@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title BKS MASTER CONTROL PLANE v5.0

cd /d "%~dp0"

for /f "delims=" %%E in ('powershell -NoProfile -Command "[char]0x1b"') do set "ESC=%%E"
set "GRN=%ESC%[92m"
set "RED=%ESC%[91m"
set "YEL=%ESC%[93m"
set "CYA=%ESC%[96m"
set "WHT=%ESC%[97m"
set "DIM=%ESC%[90m"
set "RST=%ESC%[0m"
set "ROOT=%~dp0"

goto :MENU

:: ─────────────────────────────────────────────────────────────────
:CHECK_PORT
set "PSTAT=OFFLINE"
netstat -ano 2>nul | findstr /R ":%1[^0-9]" | findstr "LISTENING" >nul 2>&1
if !errorlevel! equ 0 set "PSTAT=ONLINE"
goto :eof

:KILL_PORT
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %1 -State Listen -EA SilentlyContinue | ForEach-Object { $p=$_.OwningProcess; Stop-Process -Id $p -Force -EA SilentlyContinue; Write-Host ('    Killed PID '+$p+' porta %1') }" 2>nul
goto :eof

:FIND_PYTHON
set "PYTHON_EXE="
if exist ".venv_catalog\Scripts\python.exe" (
    ".venv_catalog\Scripts\python.exe" -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 ( set "PYTHON_EXE=.venv_catalog\Scripts\python.exe" & goto :eof )
)
if exist ".venv_dashboard\Scripts\python.exe" (
    ".venv_dashboard\Scripts\python.exe" -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 ( set "PYTHON_EXE=.venv_dashboard\Scripts\python.exe" & goto :eof )
)
goto :eof

:: ─────────────────────────────────────────────────────────────────
:MENU
cls

call :CHECK_PORT 8501
set "S1=!PSTAT!"
call :CHECK_PORT 8010
set "S2=!PSTAT!"

set /a NONL=0
if "!S1!"=="ONLINE" set /a NONL+=1
if "!S2!"=="ONLINE" set /a NONL+=1

set "D1=%RED%OFFLINE%RST%"
if "!S1!"=="ONLINE" set "D1=%GRN%ONLINE %RST%"
set "D2=%RED%OFFLINE%RST%"
if "!S2!"=="ONLINE" set "D2=%GRN%ONLINE %RST%"

set "NO_ENV="
if not exist ".env" set "NO_ENV=1"

echo.
echo  %CYA%BKS MASTER CONTROL PLANE  v5.0%RST%
echo  %DIM%bakabo.club — BKS Studio%RST%
echo  %DIM%─────────────────────────────────────────────────%RST%
echo.
echo  [!D1!]  %WHT%[1]%RST%  BKS Studio (Streamlit)   :8501
echo  [!D2!]  %WHT%[2]%RST%  Try-On AI Engine          :8010
echo.
echo  %DIM%  PC:      http://localhost:8501%RST%
echo  %DIM%  TABLET:  http://192.168.1.103:8501%RST%
echo  %DIM%─────────────────────────────────────────────────%RST%
if defined NO_ENV echo  %YEL%  [!] .env non trovato%RST%
echo.
echo  %WHT%[1]%RST% Studio  %WHT%[2]%RST% Try-On  %WHT%[A]%RST% Tutto  %WHT%[B]%RST% Browser  %WHT%[K]%RST% Kill  %WHT%[Q]%RST% Esci
echo.
set /p SCELTA=  Scelta:

if /i "!SCELTA!"=="1" goto LAUNCH_01
if /i "!SCELTA!"=="2" goto LAUNCH_02
if /i "!SCELTA!"=="A" goto LAUNCH_ALL
if /i "!SCELTA!"=="B" goto OPEN_BROWSERS
if /i "!SCELTA!"=="K" goto KILL_ALL
if /i "!SCELTA!"=="Q" exit /b 0
goto MENU

:: ─────────────────────────────────────────────────────────────────
:LAUNCH_01
echo.
echo  %GRN%Avvio BKS Studio :8501 ...%RST%
if "!S1!"=="ONLINE" (
    echo  %YEL%  Porta 8501 occupata. Kill...%RST%
    call :KILL_PORT 8501
    timeout /t 2 /nobreak >nul
)
start "BKS 01 - Studio" /d "%ROOT%" cmd /k 01_START_CATALOG_ENGINE.bat
timeout /t 8 /nobreak >nul
start http://localhost:8501
goto MENU

:LAUNCH_02
echo.
echo  %GRN%Avvio Try-On Engine :8010 ...%RST%
if "!S2!"=="ONLINE" (
    echo  %YEL%  Porta 8010 occupata. Kill...%RST%
    call :KILL_PORT 8010
    timeout /t 2 /nobreak >nul
)
start "BKS 02 - TryOn" /d "%ROOT%" cmd /k 05_START_TRYON_ENGINE.bat
timeout /t 1 /nobreak >nul
goto MENU

:: ─────────────────────────────────────────────────────────────────
:LAUNCH_ALL
cls
echo.
echo  %CYA%Avvio completo BKS...%RST%
echo.
echo  %DIM%Kill porte esistenti...%RST%
call :KILL_PORT 8501
call :KILL_PORT 8010
timeout /t 2 /nobreak >nul

echo  %DIM%[1/2]%RST% Studio :8501...
start "BKS 01 - Studio" /d "%ROOT%" cmd /k 01_START_CATALOG_ENGINE.bat
timeout /t 8 /nobreak >nul

echo  %DIM%[2/2]%RST% Try-On :8010...
start "BKS 02 - TryOn" /d "%ROOT%" cmd /k 05_START_TRYON_ENGINE.bat
timeout /t 3 /nobreak >nul

echo.
echo  %GRN%Servizi avviati. Apertura browser...%RST%
start http://localhost:8501
echo.
timeout /t 2 /nobreak >nul
goto MENU

:: ─────────────────────────────────────────────────────────────────
:OPEN_BROWSERS
if "!S1!"=="ONLINE" (
    start http://localhost:8501
    echo  %GRN%->%RST%  http://localhost:8501
)
if "!S2!"=="ONLINE" (
    start http://127.0.0.1:8010/health
    echo  %GRN%->%RST%  http://127.0.0.1:8010
)
if "!S1!"=="OFFLINE" if "!S2!"=="OFFLINE" (
    echo  %YEL%  Nessun servizio online.%RST%
)
timeout /t 2 /nobreak >nul
goto MENU

:: ─────────────────────────────────────────────────────────────────
:KILL_ALL
cls
echo.
echo  %YEL%Kill BKS su porte 8501 8010...%RST%
call :KILL_PORT 8501
call :KILL_PORT 8010
echo  %GRN%Fatto.%RST%
timeout /t 2 /nobreak >nul
goto MENU
