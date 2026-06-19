"""Quick script: fetch all Shopify products and update live CSV."""
import sys, os, requests, urllib3, csv, time
sys.path.insert(0, '.')
urllib3.disable_warnings()

from pathlib import Path
for raw in Path('.env').read_text(encoding='utf-8').splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN = os.environ['SHOPIFY_MYSHOPIFY_DOMAIN']
TOKEN  = os.environ['SHOPIFY_ADMIN_TOKEN']
VER    = os.environ.get('SHOPIFY_API_VERSION', '2025-01')
BASE   = f'https://{DOMAIN}/admin/api/{VER}'
HDR    = {'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'}

products = []
page_info = None
while True:
    if page_info:
        params = {'limit': 250, 'page_info': page_info,
                  'fields': 'id,handle,title,status,tags,variants,images'}
    else:
        params = {'limit': 250,
                  'fields': 'id,handle,title,status,tags,variants,images'}
    r = requests.get(f'{BASE}/products.json', headers=HDR, params=params,
                     timeout=30, verify=False)
    data = r.json().get('products', [])
    products.extend(data)
    print(f'  fetched {len(products)} so far...')
    link = r.headers.get('Link', '')
    if 'rel="next"' not in link:
        break
    for part in link.split(','):
        if 'rel="next"' in part:
            page_info = part.split('page_info=')[1].split('>')[0]
            break
    time.sleep(0.3)

print(f'Total: {len(products)} products')

rows = []
for p in products:
    imgs = [i['src'] for i in p.get('images', [])]
    alts = [i.get('alt', '') for i in p.get('images', [])]
    rows.append({
        'id':            str(p['id']),
        'handle':        p['handle'],
        'title':         p['title'],
        'status':        p.get('status', ''),
        'tags':          p.get('tags', ''),
        'variant_count': len(p.get('variants', [])),
        'image_count':   len(imgs),
        'image_1':       imgs[0] if imgs else '',
        'image_2':       imgs[1] if len(imgs) > 1 else '',
        'image_alts':    '|'.join(alts[:3]),
    })

Path('output').mkdir(exist_ok=True)
out = Path('output/live_shopify_products.csv')
with open(out, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f'Saved: {out}  ({len(rows)} rows)')
