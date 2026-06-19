"""Auto-rileva e attiva il CSV catalogo piu' recente."""
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from bks_assets import save_active_assets  # noqa: E402

SEARCH_DIRS = [
    BASE_DIR / "archivio",
    BASE_DIR / "collezioni_csv",
    BASE_DIR / "input",
]
DEST_DIR = BASE_DIR / "collezioni_csv"


def find_latest_csv() -> Path | None:
    files = []
    for d in SEARCH_DIRS:
        if d.exists():
            files.extend(d.glob("*.csv"))
    files = [f for f in files if f.is_file()]
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def main() -> None:
    latest = find_latest_csv()
    if latest is None:
        print("ATTENZIONE: Nessun CSV trovato in archivio/, collezioni_csv/, input/")
        sys.exit(2)  # codice 2 = no CSV (gestito dal bat con messaggio friendly)

    print(f"CSV trovato: {latest}")

    dest = DEST_DIR / latest.name
    if latest.resolve() != dest.resolve():
        DEST_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(latest, dest)
        print(f"Copiato in: {dest.relative_to(BASE_DIR)}")
        active = dest
    else:
        active = latest

    save_active_assets(catalog_csv=active)
    print(f"OK - Catalogo attivato: {active.name}")


if __name__ == "__main__":
    main()
