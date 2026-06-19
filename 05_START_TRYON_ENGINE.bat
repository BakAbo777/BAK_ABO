@echo off
title BKS Tryon Engine — porta 8010
echo.
echo  BKS TRYON REALTIME ENGINE v0.2
echo  Porta: 8010
echo  Modello: gpt-image-1
echo.

set "ENGINE_DIR=%~dp0tryon_engine\BAKABO_TRYON_REALTIME_ENGINE_v0_2"
set "UVICORN=%~dp0.venv_catalog\Scripts\uvicorn.exe"

if not exist "%UVICORN%" (
  echo [ERRORE] uvicorn non trovato in .venv_catalog
  pause
  exit /b 1
)

if not exist "%ENGINE_DIR%\.env" (
  echo [ERRORE] .env mancante in tryon_engine\BAKABO_TRYON_REALTIME_ENGINE_v0_2
  pause
  exit /b 1
)

cd /d "%ENGINE_DIR%"
echo  Avvio FastAPI su http://127.0.0.1:8010
echo  Premi Ctrl+C per fermare.
echo.
"%UVICORN%" api.main:app --host 127.0.0.1 --port 8010 --reload
pause
