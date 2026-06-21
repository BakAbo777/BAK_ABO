@echo off
chcp 65001 >nul
echo.
echo  BKS Studio — YouTube OAuth Setup
echo  ─────────────────────────────────
echo  Avvia il browser per autorizzare l'accesso YouTube.
echo  Dopo l'autorizzazione il canale verra' rinominato "BKS Studio".
echo.
cd /d "I:\BAK ABO"
call .venv\Scripts\activate.bat 2>nul || call venv\Scripts\activate.bat 2>nul
python scripts/youtube_oauth_setup.py %*
echo.
pause
