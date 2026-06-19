"""
BKS unified database — SQLite store built from output/ CSV/JSON files.

Usage:
    from ecommerce_automation.bks_db import bks_db
    rows = bks_db.query("SELECT * FROM bks_collection_plan_v20 LIMIT 5")
    bks_db.rebuild()   # re-import all source files
"""
import os, sys, json, csv, sqlite3, shutil, glob
from pathlib import Path
from datetime import datetime

OUTPUT = Path(__file__).resolve().parent.parent / "output"
DB_PATH = OUTPUT / "bks_database.sqlite"
ARCHIVE_LOGS = OUTPUT / "99_ARCHIVIO" / "logs"

# CSVs that should not be imported (too large, binary-adjacent, or truly ephemeral)
SKIP_CSV = {
    "bakabo_export_package.zip",
}

def _table_name(fname: str) -> str:
    """Derive a clean SQLite table name from a filename."""
    stem = Path(fname).stem
    # Remove version suffixes like _v20, replace non-word chars with _
    import re
    return re.sub(r"[^\w]", "_", stem).strip("_")

def _import_csv(conn: sqlite3.Connection, csv_path: Path) -> str | None:
    """Import a CSV file as a SQLite table. Returns table name or None on failure."""
    tname = _table_name(csv_path.name)
    try:
        with open(csv_path, encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return None
            cols = [c.strip() for c in reader.fieldnames if c]
            if not cols:
                return None
            rows = list(reader)
        import re
        safe_cols = [re.sub(r"[^\w]", "_", c).strip("_") or f"col{i}" for i, c in enumerate(cols)]
        col_defs = ", ".join(f'"{c}" TEXT' for c in safe_cols)
        conn.execute(f'DROP TABLE IF EXISTS "{tname}"')
        conn.execute(f'CREATE TABLE "{tname}" ({col_defs})')
        placeholders = ", ".join("?" * len(safe_cols))
        for row in rows:
            vals = [row.get(cols[i], "") for i in range(len(cols))]
            conn.execute(f'INSERT INTO "{tname}" VALUES ({placeholders})', vals)
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS _bks_catalog (
                table_name TEXT PRIMARY KEY,
                source_file TEXT,
                row_count INTEGER,
                col_count INTEGER,
                imported_at TEXT
            )
        ''')
        conn.execute(
            'INSERT OR REPLACE INTO _bks_catalog VALUES (?,?,?,?,?)',
            (tname, str(csv_path.name), len(rows), len(cols),
             datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        return tname
    except Exception as e:
        print(f"  SKIP {csv_path.name}: {e}", file=sys.stderr)
        return None

def _import_json_flat(conn: sqlite3.Connection, json_path: Path) -> list[str]:
    """Import JSON files that contain list-of-dicts or dict-of-lists as tables."""
    imported = []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
        tname = _table_name(json_path.name)
        import re

        def _load_records(records: list, tname: str):
            if not records or not isinstance(records[0], dict):
                return
            all_keys = []
            for r in records:
                for k in r.keys():
                    if k not in all_keys:
                        all_keys.append(k)
            raw = [re.sub(r"[^\w]", "_", k).strip("_") or f"col{i}"
                   for i, k in enumerate(all_keys)]
            # Deduplicate column names
            seen_c: dict[str, int] = {}
            safe_cols = []
            for c in raw:
                if c in seen_c:
                    seen_c[c] += 1
                    safe_cols.append(f"{c}_{seen_c[c]}")
                else:
                    seen_c[c] = 0
                    safe_cols.append(c)
            col_defs = ", ".join(f'"{c}" TEXT' for c in safe_cols)
            conn.execute(f'DROP TABLE IF EXISTS "{tname}"')
            conn.execute(f'CREATE TABLE "{tname}" ({col_defs})')
            ph = ", ".join("?" * len(all_keys))
            for r in records:
                vals = [str(r.get(k, "")) if not isinstance(r.get(k, ""), str)
                        else r.get(k, "") for k in all_keys]
                conn.execute(f'INSERT INTO "{tname}" VALUES ({ph})', vals)
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS _bks_catalog (
                    table_name TEXT PRIMARY KEY,
                    source_file TEXT,
                    row_count INTEGER,
                    col_count INTEGER,
                    imported_at TEXT
                )
            ''')
            conn.execute(
                'INSERT OR REPLACE INTO _bks_catalog VALUES (?,?,?,?,?)',
                (tname, json_path.name, len(records), len(all_keys),
                 datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
            imported.append(tname)

        if isinstance(data, list):
            _load_records(data, tname)
        elif isinstance(data, dict):
            # Try top-level as records
            items = list(data.items())
            rows_from_vals = []
            for k, v in items:
                if isinstance(v, dict):
                    v["_key"] = k
                    rows_from_vals.append(v)
                elif isinstance(v, list) and all(isinstance(i, dict) for i in v):
                    for rec in v:
                        rec["_collection"] = k
                    rows_from_vals.extend(v)
                else:
                    rows_from_vals.append({"key": k, "value": str(v)})
            _load_records(rows_from_vals, tname)
    except Exception as e:
        print(f"  SKIP {json_path.name}: {e}", file=sys.stderr)
    return imported

def rebuild(verbose: bool = True) -> dict:
    """Re-import all output/ CSV/JSON files into bks_database.sqlite."""
    # Archive log files first
    ARCHIVE_LOGS.mkdir(parents=True, exist_ok=True)
    archived = []
    for pat in ("*.log", "*.err", "*.err.log", "*.out.log"):
        for f in OUTPUT.glob(pat):
            dst = ARCHIVE_LOGS / f.name
            if not dst.exists():
                shutil.move(str(f), str(dst))
                archived.append(f.name)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    tables = []
    skipped = []

    # Import all CSVs in output/ root
    for csv_file in sorted(OUTPUT.glob("*.csv")):
        if csv_file.name in SKIP_CSV:
            continue
        t = _import_csv(conn, csv_file)
        if t:
            tables.append(t)
        else:
            skipped.append(csv_file.name)

    # Import key JSONs
    key_jsons = [
        "bks_ai_index.json",
        "bks_collection_payloads_v20.json",
        "always_on_agent_status.json",
        "realtime_control_status.json",
        "network_monitor_report.json",
        "bks_main_menu_base_config.json",
        "bks_active_assets.json",
        "daily_web_update.json",
        "dialogic_agent_protocol.json",
    ]
    for jname in key_jsons:
        jp = OUTPUT / jname
        if jp.exists():
            ts = _import_json_flat(conn, jp)
            tables.extend(ts)
            if not ts:
                skipped.append(jname)

    # Create master files index
    conn.execute("DROP TABLE IF EXISTS _bks_files")
    conn.execute("""
        CREATE TABLE _bks_files (
            filename TEXT,
            subdir TEXT,
            ext TEXT,
            size_kb REAL,
            modified TEXT
        )
    """)
    for root, dirs, files in os.walk(OUTPUT):
        dirs[:] = [d for d in dirs if d != ".git"]
        rel = os.path.relpath(root, OUTPUT)
        for f in files:
            fp = Path(root) / f
            stat = fp.stat()
            conn.execute(
                "INSERT INTO _bks_files VALUES (?,?,?,?,?)",
                (f, rel, fp.suffix, round(stat.st_size / 1024, 1),
                 datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"))
            )

    conn.commit()
    conn.close()

    result = {
        "db": str(DB_PATH),
        "tables": len(tables),
        "archived_logs": len(archived),
        "skipped": skipped,
        "table_list": tables,
    }
    if verbose:
        print(f"BKS database built: {len(tables)} tables, {len(archived)} logs archived")
        print(f"  DB: {DB_PATH}")
        if skipped:
            print(f"  Skipped: {skipped}")
    return result

def query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT query and return list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_table(name: str) -> list[dict]:
    """Fetch all rows from a table."""
    return query(f'SELECT * FROM "{name}"')

def list_tables() -> list[str]:
    """List all user tables (excludes internal _bks_* tables)."""
    rows = query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '_bks_%'")
    return [r["name"] for r in rows]

def catalog() -> list[dict]:
    """Return the import catalog with row/col counts per table."""
    return query("SELECT * FROM _bks_catalog ORDER BY table_name")

# Auto-rebuild if DB doesn't exist
if not DB_PATH.exists():
    rebuild(verbose=False)

# Module-level singleton
class _BksDb:
    query = staticmethod(query)
    get_table = staticmethod(get_table)
    list_tables = staticmethod(list_tables)
    catalog = staticmethod(catalog)
    rebuild = staticmethod(rebuild)
    db_path = DB_PATH

bks_db = _BksDb()

if __name__ == "__main__":
    result = rebuild()
    print(f"\nTables ({result['tables']}):")
    for t in sorted(result["table_list"]):
        print(f"  {t}")
