@echo off
chcp 65001 >nul
echo.
echo  BKS Studio — YouTube Video Optimizer
echo  ──────────────────────────────────────
echo  Modalita: DRY RUN (solo analisi, nessuna modifica)
echo  Usa --apply per applicare le modifiche.
echo.
cd /d "I:\BAK ABO"
call .venv\Scripts\activate.bat 2>nul || call venv\Scripts\activate.bat 2>nul
python scripts/youtube_optimize_videos.py %*
echo.
pause
