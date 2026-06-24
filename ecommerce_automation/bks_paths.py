"""BKS system root paths — common reference for all scripts."""
from pathlib import Path

BKS_ROOT     = Path("I:/BAK ABO")
BKS_DATABASE = Path("I:/BKS database")
BAKABO_SYS   = Path("I:/BAKABO SYSTEM")

# Wonder image archives
WONDER_NFT_ARCHIVE    = BKS_DATABASE / "BKS_ORGANIZED_20260615_225737" / "01_NFT"
WONDER_FACTORY_CACHE  = BKS_ROOT / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "printify_library" / "designs"
BLUEPRINT_TEMPLATES   = BKS_DATABASE  # each subfolder = blueprint_id with .ai/.psd templates

# Runtime data
VERSE_DB     = BAKABO_SYS / "data" / "verse.db"
VERSE_API    = "http://localhost:8001"

def env(key: str, fallback: str = "") -> str:
    import os
    if key in os.environ:
        return os.environ[key]
    env_path = BKS_ROOT / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            if k.strip() == key:
                return v.strip()
    return fallback
