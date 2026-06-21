@echo off
chcp 65001 >nul
echo.
echo ══════════════════════════════════════════
echo   BKS — Deploy Header Snippet
echo   snippets/bakabo-header.liquid
echo ══════════════════════════════════════════
echo.

cd /d "I:\BAK ABO"

python -c "
import os, sys, base64, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
ROOT = Path('I:/BAK ABO')
for raw in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line: continue
    k, v = line.split('=', 1)
    k = k.strip(); v = v.strip().strip('\"').strip(\"'\")
    if k not in os.environ: os.environ[k] = v

DOMAIN  = os.environ['SHOPIFY_MYSHOPIFY_DOMAIN']
TOKEN   = os.environ['SHOPIFY_ADMIN_TOKEN']
VERSION = os.environ.get('SHOPIFY_API_VERSION', '2025-01')
BASE    = f'https://{DOMAIN}/admin/api/{VERSION}'
HDR     = {'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'}

# Get active theme ID
r = requests.get(f'{BASE}/themes.json', headers=HDR, verify=False)
themes = r.json().get('themes', [])
active = next((t for t in themes if t['role'] == 'main'), None)
if not active:
    print('ERRORE: nessun tema attivo trovato.')
    sys.exit(1)
theme_id = active['id']
print(f'Tema attivo: {active[\"name\"]} (ID {theme_id})')

# Deploy bakabo-header.liquid
local_path = ROOT / '04_TEMA_SHOPIFY' / 'snippets' / 'bakabo-header.liquid'
shopify_key = 'snippets/bakabo-header.liquid'
content = local_path.read_text(encoding='utf-8')
encoded = base64.b64encode(content.encode('utf-8')).decode()

payload = {'asset': {'key': shopify_key, 'attachment': encoded}}
url = f'{BASE}/themes/{theme_id}/assets.json'
resp = requests.put(url, headers=HDR, json=payload, verify=False)
if resp.status_code in (200, 201):
    print(f'  DEPLOYATO: {shopify_key}')
else:
    print(f'  ERRORE {resp.status_code}: {resp.text[:200]}')
    sys.exit(1)

print()
print('Deploy completato. Verifica su: https://bakabo.club')
"

echo.
pause
