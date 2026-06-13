@echo off
chcp 65001 >nul
title BKS 04 - Image Factory v1.1

cd /d "%~dp0BAKABO_IMAGE_FACTORY_v1.1"

echo.
echo  BKS 04 - IMAGE FACTORY v1.1
echo  ===========================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creo ambiente venv...
    py -m venv venv
    if %errorlevel% neq 0 (
        python -m venv venv
    )
    if %errorlevel% neq 0 (
        echo ERRORE: impossibile creare venv.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente venv presente.
)

call venv\Scripts\activate.bat

echo [2/3] Verifico dipendenze Image Factory...
python -c "import streamlit, PIL, requests, dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERRORE: installazione dipendenze fallita.
        pause
        exit /b 1
    )
) else (
    echo Dipendenze presenti.
)

echo.
echo [3/3] Avvio Image Factory...
echo Apri: http://localhost:8503
echo.

start /b "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8503"
streamlit run app.py --server.port 8503 --browser.gatherUsageStats false

pause
