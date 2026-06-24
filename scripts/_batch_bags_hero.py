"""
Rigenera bks_hero SOLO per Bags e Travel Bag con la pipeline v3
(3-pass flood fill: edge + near-neutral expansion top/bottom + zone chiuse).
Cancella i vecchi record DB prima di rielaborare.
"""
from __future__ import annotations
import os, time, base64, sqlite3, json, requests, urllib3
from collections import deque
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

SHOPIFY_DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
PRINTIFY_TOKEN = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID        = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_VER         = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
SH_BASE        = f"https://{SHOPIFY_DOMAIN}/admin/api/{SH_VER}"
SH_GET         = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
SH_POST        = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
PY_HDR         = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json;charset=utf-8"}

TARGET_TYPES = {"Bags", "Travel Bag"}

COLLECTION_COLORS = {
    "bks-hours":(200,196,190),"bks-glyph":(212,160,48),"bks-marker":(192,68,24),
    "bks-riviera":(12,168,152),"bks-pulse":(136,136,204),"bks-token":(152,40,216),
    "bks-flag":(200,32,32),"bks-origin":(72,152,8),
}
_SHORT = {k.replace("bks-",""): k for k in COLLECTION_COLORS}
PAPER  = (250, 250, 247)
BAG_BLEND = 0.40
CANVAS = 1200
PAD    = 120

OUT_DIR = ROOT / "output" / "catalog_images" / "bks_hero"
OUT_DIR.mkdir(parents=True, exist_ok=True)

asset_meta = json.loads((ROOT / "output" / "bks_active_assets.json").read_text())
db_path    = asset_meta.get("catalog_db", "")
conn       = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

def resolve_col(tags):
    for t in tags:
        if t in COLLECTION_COLORS: return t
        if t.startswith("collection:"):
            s = t[len("collection:"):]
            if s in _SHORT: return _SHORT[s]
    return None

def tinted_bg(col):
    base = COLLECTION_COLORS.get(col, (200,200,195))
    return tuple(int(base[i]+(PAPER[i]-base[i])*BAG_BLEND) for i in range(3))

def remove_white_bg(img: Image.Image, thresh: int = 240) -> Image.Image:
    rgba = img.convert("RGBA")
    arr  = np.array(rgba, dtype=np.uint8)
    h, w = arr.shape[:2]
    lum  = (0.299*arr[:,:,0].astype(np.float32)
           +0.587*arr[:,:,1].astype(np.float32)
           +0.114*arr[:,:,2].astype(np.float32))
    r_ch = arr[:,:,0].astype(np.float32)
    g_ch = arr[:,:,1].astype(np.float32)
    b_ch = arr[:,:,2].astype(np.float32)
    chroma = (np.maximum(np.maximum(r_ch,g_ch),b_ch)
             -np.minimum(np.minimum(r_ch,g_ch),b_ch))
    is_bg = lum >= thresh

    # Pass 1: edge flood fill
    visited = np.zeros((h,w), dtype=bool)
    queue   = deque()
    for x in range(w):
        for yr in (0,h-1):
            if is_bg[yr,x] and not visited[yr,x]:
                visited[yr,x]=True; queue.append((yr,x))
    for y in range(h):
        for xr in (0,w-1):
            if is_bg[y,xr] and not visited[y,xr]:
                visited[y,xr]=True; queue.append((y,xr))
    while queue:
        cy,cx=queue.popleft()
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<h and 0<=nx<w and not visited[ny,nx] and is_bg[ny,nx]:
                visited[ny,nx]=True; queue.append((ny,nx))

    # Pass 1.5: near-neutral expansion (top 20% + bottom 35%)
    top_end   = int(h*0.20)
    bot_start = int(h*0.65)
    shadow_cand = (lum >= 170) & (chroma < 12) & ~visited

    def _expand(row_min, row_max):
        q = deque()
        for y in range(row_min, row_max):
            for x in range(w):
                if shadow_cand[y,x]:
                    for dy2,dx2 in ((-1,0),(1,0),(0,-1),(0,1)):
                        ny2,nx2=y+dy2,x+dx2
                        if 0<=ny2<h and 0<=nx2<w and visited[ny2,nx2]:
                            visited[y,x]=True; q.append((y,x)); break
        while q:
            cy,cx=q.popleft()
            for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
                ny,nx=cy+dy,cx+dx
                if row_min<=ny<row_max and 0<=nx<w and not visited[ny,nx] and shadow_cand[ny,nx]:
                    visited[ny,nx]=True; q.append((ny,nx))

    _expand(0, top_end)
    _expand(bot_start, h)

    alpha = np.full((h,w),255,dtype=np.uint8)
    alpha[visited] = 0
    for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
        border = np.roll(visited,(dy,dx),axis=(0,1)) & ~visited
        alpha[border] = np.minimum(alpha[border], 64)

    # Pass 2: zone chiuse interne near-neutral
    inner_bg = (lum >= 242) & (chroma < 20) & ~visited
    if inner_bg.any():
        labeled = np.zeros((h,w),dtype=np.int32)
        lid = 0
        for sy in range(h):
            for sx in range(w):
                if inner_bg[sy,sx] and labeled[sy,sx]==0:
                    lid+=1
                    q2=deque([(sy,sx)]); labeled[sy,sx]=lid
                    while q2:
                        cy2,cx2=q2.popleft()
                        for dy2,dx2 in ((-1,0),(1,0),(0,-1),(0,1)):
                            ny2,nx2=cy2+dy2,cx2+dx2
                            if 0<=ny2<h and 0<=nx2<w and inner_bg[ny2,nx2] and labeled[ny2,nx2]==0:
                                labeled[ny2,nx2]=lid; q2.append((ny2,nx2))
        inner_mask = labeled > 0
        alpha[inner_mask] = 0
        visited = visited | inner_mask

    arr[:,:,3] = alpha
    arr[visited,:3] = 0
    return Image.fromarray(arr,"RGBA")

def make_gradient_bg(size, top_rgb, bot_rgb):
    arr = np.zeros((size,size,3),dtype=np.uint8)
    for y in range(size):
        t = y/(size-1)
        for c in range(3): arr[y,:,c] = int(top_rgb[c]+(bot_rgb[c]-top_rgb[c])*t)
    return Image.fromarray(arr,"RGB").convert("RGBA")

def compose(fg, bg_rgb, rot=0.0):
    LIGHT = (250,250,247)
    top_c = tuple(int(bg_rgb[i]+(LIGHT[i]-bg_rgb[i])*0.45) for i in range(3))
    bot_c = tuple(int(bg_rgb[i]*0.88) for i in range(3))
    if rot: fg = fg.rotate(rot, resample=Image.BICUBIC, expand=True)
    fg.thumbnail((CANVAS-2*PAD, CANVAS-2*PAD), Image.LANCZOS)
    bg = make_gradient_bg(CANVAS, top_c, bot_c)
    alpha = fg.split()[3]
    sh_a  = alpha.filter(ImageFilter.GaussianBlur(22))
    sh_a  = sh_a.point(lambda p: min(60, int(p*0.7)))
    sl = Image.new("RGBA", fg.size, (20,20,20,0)); sl.putalpha(sh_a)
    sh = Image.new("RGBA", fg.size, (0,0,0,0)); sh.paste(sl,(0,18),mask=sh_a)
    x = (CANVAS-fg.width)//2; y = (CANVAS-fg.height)//2
    bg.paste(sh,(x,y+8),mask=sh); bg.paste(fg,(x,y),mask=fg)
    return bg.convert("RGB")

def get_ghost_url(py_prod):
    imgs = py_prod.get("images", [])
    for lbl in ["front","back","closeup"]:
        for img in imgs:
            src = img.get("src","")
            if f"camera_label={lbl}" in src.lower() and "on-person" not in src.lower():
                return src
    for img in imgs:
        if "on-person" not in img.get("src","").lower(): return img.get("src")
    return imgs[0]["src"] if imgs else None

def upload_img(product_id, img_path):
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    r = requests.post(f"{SH_BASE}/products/{product_id}/images.json",
        headers=SH_POST,
        json={"image":{"attachment":b64,"filename":img_path.name,"position":2}},
        timeout=40, verify=False)
    if r.status_code in (200,201):
        return r.json().get("image",{}).get("src","")
    print(f"  upload FAIL {r.status_code}: {r.text[:80]}")
    return None

# ── Carica prodotti ──────────────────────────────────────────────────────────
print("Carico Shopify...")
sh_all = []
url = f"{SH_BASE}/products.json"
params = {"status":"active","limit":250,"fields":"id,handle,tags,product_type"}
while url:
    r = requests.get(url, headers=SH_GET, params=params, verify=False, timeout=20)
    sh_all.extend(r.json().get("products",[]))
    link = r.headers.get("Link",""); url = None; params = {}
    if 'rel="next"' in link:
        for part in link.split(","):
            if 'rel="next"' in part: url = part.strip().split(";")[0].strip("<> "); break
    time.sleep(0.3)

bags = [p for p in sh_all if p.get("product_type","").strip() in TARGET_TYPES]
print(f"  Bag/Travel Bag trovati: {len(bags)}")

print("Carico Printify...")
py_all = []
for pg in range(1,20):
    d = requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                     headers=PY_HDR, params={"page":pg,"limit":50}, verify=False).json()
    batch = d.get("data",[]);
    if not batch: break
    py_all.extend(batch)
    if pg >= int(d.get("last_page",pg)): break
    time.sleep(0.3)
py_map = {str((p.get("external") or {}).get("id","")): p for p in py_all}

# ── Cancella vecchi record DB per bag ────────────────────────────────────────
bag_handles = [p["handle"] for p in bags]
conn.execute(
    f"DELETE FROM assets WHERE asset_type='bks_hero' AND product_handle IN ({','.join('?'*len(bag_handles))})",
    bag_handles
)
conn.commit()
print(f"  Vecchi record DB rimossi: {conn.execute('SELECT changes()').fetchone()[0]}")

# ── Build eligible list ───────────────────────────────────────────────────────
eligible = []
for sh in bags:
    tags = [t.strip().lower() for t in sh.get("tags","").split(",")]
    col  = resolve_col(tags)
    if not col: continue
    py_p = py_map.get(str(sh["id"]))
    if not py_p: continue
    ghost = get_ghost_url(py_p)
    if not ghost: continue
    eligible.append({"shopify_id":sh["id"],"handle":sh["handle"],"col":col,"ptype":sh.get("product_type","").strip(),"ghost":ghost})

print(f"\nEligibili: {len(eligible)} bag\n")
ok = err = 0

for i, prod in enumerate(eligible, 1):
    handle = prod["handle"]; col = prod["col"]; ptype = prod["ptype"]
    bg = tinted_bg(col); rot = (hash(handle)%7)-3
    print(f"[{i:3d}/{len(eligible)}] {handle[:50]} [{col}] rot={rot:+d}")
    try:
        r = requests.get(prod["ghost"], timeout=20, verify=False)
        if r.status_code != 200: print(f"  SKIP {r.status_code}"); err+=1; continue
        src = Image.open(BytesIO(r.content)).convert("RGB")
        fg  = remove_white_bg(src)
        out_img = compose(fg, bg, rot)
        d = OUT_DIR / handle; d.mkdir(exist_ok=True)
        out_p = d / f"{handle}_hero.png"
        out_img.save(out_p, "PNG", optimize=True)
        print(f"  gen OK  {out_p.stat().st_size//1024} KB")
        time.sleep(0.3)
        cdn = upload_img(prod["shopify_id"], out_p)
        if cdn:
            ok+=1; print(f"  upload OK")
            conn.execute(
                "INSERT OR REPLACE INTO assets (product_handle,asset_type,collection,file_path,url,meta_json) VALUES (?,?,?,?,?,?)",
                (handle,"bks_hero",col,str(out_p),cdn,json.dumps({"product_type":ptype,"source":"ghost_front","pipeline":"v3"}))
            )
            conn.commit()
    except Exception as ex:
        import traceback; print(f"  ERROR: {ex}"); traceback.print_exc(); err+=1
    time.sleep(0.5)

conn.close()
print(f"\n{'='*50}\nUpload OK: {ok}/{len(eligible)}  Errori: {err}")
