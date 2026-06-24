"""Test scontornamento bag/backpack — 3 passaggi flood fill."""
from __future__ import annotations
import os, requests, urllib3
from io import BytesIO
from pathlib import Path
from collections import deque
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

SH_DOM  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SH_TOK  = os.environ["SHOPIFY_ADMIN_TOKEN"]
PY_TOK  = os.environ["PRINTIFY_API_TOKEN"]
SHOP_ID = os.environ.get("PRINTIFY_SHOP_ID", "12030061")
SH_HDR  = {"X-Shopify-Access-Token": SH_TOK}
PY_HDR  = {"Authorization": f"Bearer {PY_TOK}"}

COLS = {"bks-hours","bks-glyph","bks-marker","bks-riviera",
        "bks-pulse","bks-token","bks-flag","bks-origin"}
SHORT_TO_BKS = {k.replace("bks-",""): k for k in COLS}
PAPER = (250, 250, 247)
COLLECTION_COLORS = {
    "bks-hours":(200,196,190),"bks-glyph":(212,160,48),"bks-marker":(192,68,24),
    "bks-riviera":(12,168,152),"bks-pulse":(136,136,204),"bks-token":(152,40,216),
    "bks-flag":(200,32,32),"bks-origin":(72,152,8),
}
PRODUCT_TYPE_BLEND = {"Bags":0.40,"Travel Bag":0.40,"Backpack":0.40}

def resolve_col(tags):
    for t in tags:
        if t in COLS: return t
        if t.startswith("collection:"):
            s = t[len("collection:"):]
            if s in SHORT_TO_BKS: return SHORT_TO_BKS[s]
    return None

def tinted(col, ptype):
    base  = COLLECTION_COLORS.get(col,(200,200,195))
    blend = PRODUCT_TYPE_BLEND.get(ptype,0.45)
    return tuple(int(base[i]+(PAPER[i]-base[i])*blend) for i in range(3))

def remove_white_bg(img: Image.Image, thresh: int = 240) -> Image.Image:
    """3 passaggi: edge BFS | bottom shadow | zone chiuse interne."""
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
            - np.minimum(np.minimum(r_ch,g_ch),b_ch))
    is_bg  = lum >= thresh

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

    # Pass 1.5: near-neutral expansion da visited (top 20% + bottom 35%)
    top_zone_end    = int(h * 0.20)
    shadow_row_start = int(h * 0.65)
    shadow_cand = (lum >= 170) & (chroma < 12) & ~visited

    def _expand_nn(row_min, row_max):
        sh_q = deque()
        for y in range(row_min, row_max):
            for x in range(w):
                if shadow_cand[y, x]:
                    for dy2,dx2 in ((-1,0),(1,0),(0,-1),(0,1)):
                        ny2,nx2=y+dy2,x+dx2
                        if 0<=ny2<h and 0<=nx2<w and visited[ny2,nx2]:
                            visited[y,x]=True; sh_q.append((y,x)); break
        while sh_q:
            cy,cx=sh_q.popleft()
            for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
                ny,nx=cy+dy,cx+dx
                if row_min<=ny<row_max and 0<=nx<w and not visited[ny,nx] and shadow_cand[ny,nx]:
                    visited[ny,nx]=True; sh_q.append((ny,nx))

    _expand_nn(0, top_zone_end)
    _expand_nn(shadow_row_start, h)

    alpha = np.full((h,w),255,dtype=np.uint8)
    alpha[visited] = 0
    for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
        border = np.roll(visited,(dy,dx),axis=(0,1)) & ~visited
        alpha[border] = np.minimum(alpha[border], 64)

    # Pass 2: zone chiuse interne near-neutral (anello top, foro manico)
    inner_thresh = 242
    inner_bg = (lum >= inner_thresh) & (chroma < 20) & ~visited
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

def make_gradient_bg(size,top_rgb,bot_rgb):
    arr=np.zeros((size,size,3),dtype=np.uint8)
    for y in range(size):
        t=y/(size-1)
        for c in range(3): arr[y,:,c]=int(top_rgb[c]+(bot_rgb[c]-top_rgb[c])*t)
    return Image.fromarray(arr,"RGB").convert("RGBA")

def compose(fg,bg_rgb,rot=0.0):
    CANVAS,PAD=1200,120
    LIGHT=(250,250,247)
    top_c=tuple(int(bg_rgb[i]+(LIGHT[i]-bg_rgb[i])*0.45) for i in range(3))
    bot_c=tuple(int(bg_rgb[i]*0.88) for i in range(3))
    if rot: fg=fg.rotate(rot,resample=Image.BICUBIC,expand=True)
    fg.thumbnail((CANVAS-2*PAD,CANVAS-2*PAD),Image.LANCZOS)
    bg=make_gradient_bg(CANVAS,top_c,bot_c)
    shadow_a=fg.split()[3].filter(ImageFilter.GaussianBlur(22))
    shadow_a=shadow_a.point(lambda p:min(60,int(p*0.7)))
    sl=Image.new("RGBA",fg.size,(20,20,20,0)); sl.putalpha(shadow_a)
    sh=Image.new("RGBA",fg.size,(0,0,0,0)); sh.paste(sl,(0,18),mask=shadow_a)
    x=(CANVAS-fg.width)//2; y=(CANVAS-fg.height)//2
    bg.paste(sh,(x,y+8),mask=sh); bg.paste(fg,(x,y),mask=fg)
    return bg.convert("RGB")

# ── Load ─────────────────────────────────────────────────────────────────────
r=requests.get(f"https://{SH_DOM}/admin/api/2025-01/products.json",headers=SH_HDR,
    params={"status":"active","limit":250,"fields":"id,handle,tags,product_type"},verify=False)
sh_prods=r.json().get("products",[])

all_py=[]
for page in range(1,20):
    d=requests.get(f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json",
                   headers=PY_HDR,params={"page":page,"limit":50},verify=False).json()
    batch=d.get("data",[]);
    if not batch: break
    all_py.extend(batch)
    if page>=int(d.get("last_page",page)): break
py_map={str((p.get("external") or {}).get("id","")): p for p in all_py}

OUT=ROOT/"output"/"catalog_images"/"bag_test"; OUT.mkdir(parents=True,exist_ok=True)

# Seleziona campioni: Bags + Travel Bag + Backpack
bag_types={"Bags","Travel Bag","Backpack"}
samples=[]; seen_type_col=set()
for sh in sh_prods:
    ptype=sh.get("product_type","").strip()
    if ptype not in bag_types: continue
    tags=[t.strip().lower() for t in sh.get("tags","").split(",")]
    col=resolve_col(tags)
    if not col: continue
    key=(ptype, col)
    if key in seen_type_col: continue
    py_p=py_map.get(str(sh["id"]))
    if not py_p: continue
    imgs=py_p.get("images",[])
    ghost=None
    for lbl in ["front","back","closeup"]:
        for img in imgs:
            src=img.get("src","")
            if f"camera_label={lbl}" in src and "on-person" not in src:
                ghost=src; break
        if ghost: break
    if not ghost:
        for img in imgs:
            if "on-person" not in img.get("src",""): ghost=img.get("src"); break
    if not ghost: continue
    seen_type_col.add(key)
    samples.append({"handle":sh["handle"],"col":col,"ptype":ptype,"ghost":ghost})
    if len(samples)>=6: break

print(f"Campioni bag/backpack: {len(samples)}\n")
for s in samples:
    handle,col,ptype=s["handle"],s["col"],s["ptype"]
    bg=tinted(col,ptype)
    rot=(hash(handle)%7)-3
    print(f"  [{ptype}] {handle} [{col}] rot={rot:+d}deg")
    img_bytes=requests.get(s["ghost"],timeout=20,verify=False).content
    src_img=Image.open(BytesIO(img_bytes)).convert("RGB")
    fg=remove_white_bg(src_img)
    result=compose(fg,bg,rot)
    out=OUT/f"{ptype.replace(' ','_')}_{handle[:30]}_test.png"
    result.save(out,"PNG",optimize=True)
    print(f"  -> {out.name}  {out.stat().st_size//1024} KB")

print(f"\nOutput: {OUT}")
