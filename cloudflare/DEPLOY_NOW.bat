@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM  BKS Agent — Cloudflare Worker Setup (v2)
REM
REM  OPZIONE A (consigliata): usa setup_worker.py con API Token
REM    1. Vai su https://dash.cloudflare.com/profile/api-tokens
REM    2. "Create Token" > "Edit Cloudflare Workers" > copia il token
REM    3. Esegui: SET CLOUDFLARE_API_TOKEN=il_tuo_token
REM    4. Esegui: python cloudflare/setup_worker.py
REM
REM  OPZIONE B: usa wrangler login (apre browser)
REM    1. Esegui: wrangler login   (nella cartella cloudflare/)
REM    2. Poi esegui: wrangler kv namespace create "BKS_AGENT_KV"
REM    3. Copia l'ID nel wrangler.toml (riga id = "SOSTITUIRE_...")
REM    4. Esegui: wrangler deploy
REM    5. Imposta i secrets con: wrangler secret put NOME_SECRET
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0\.."

echo.
echo [BKS] Cloudflare Worker Setup
echo.
echo Hai un CLOUDFLARE_API_TOKEN impostato?
echo.

IF "%CLOUDFLARE_API_TOKEN%"=="" (
    echo CLOUDFLARE_API_TOKEN non trovato.
    echo.
    echo Ottienilo da: https://dash.cloudflare.com/profile/api-tokens
    echo Poi esegui:
    echo   set CLOUDFLARE_API_TOKEN=il_tuo_token
    echo   python cloudflare\setup_worker.py
    echo.
    echo --- OPPURE usa wrangler login (apre browser) ---
    echo   cd cloudflare
    echo   wrangler login
    echo   wrangler kv namespace create "BKS_AGENT_KV"
    echo   [copia ID in wrangler.toml]
    echo   wrangler deploy
    echo.
    pause
    exit /b 0
)

echo CLOUDFLARE_API_TOKEN trovato — esecuzione setup automatico...
echo.
python cloudflare\setup_worker.py
pause
