"""The Ledger: every build logged to the Konoha Archives (Supabase).
Falls back to local sqlite if the archive seals are missing (tests, offline)."""
import os
import sqlite3
from datetime import date

from dotenv import load_dotenv
load_dotenv()

DB_PATH = "builds.db"
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_KEY")
USE_SUPABASE = bool(URL and KEY)

if USE_SUPABASE:
    from supabase import create_client
    sb = create_client(URL, KEY)

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS builds("
        "id INTEGER PRIMARY KEY, ts TEXT, brief TEXT, style TEXT, "
        "score INTEGER, zip_path TEXT)"
    )
    return conn

def log_build(brief, style, score, zip_path):
    if USE_SUPABASE:
        sb.table("builds").insert(
            {"brief": brief, "style": style, "score": score, "zip_path": zip_path}
        ).execute()
        return
    conn = _conn()
    conn.execute(
        "INSERT INTO builds(ts, brief, style, score, zip_path) "
        "VALUES (datetime('now','localtime'), ?, ?, ?, ?)",
        (brief, style, score, zip_path),
    )
    conn.commit()
    conn.close()

def builds_today():
    if USE_SUPABASE:
        r = sb.table("builds").select("id", count="exact") \
              .gte("ts", date.today().isoformat()).execute()
        return r.count or 0
    conn = _conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM builds WHERE date(ts) = date('now','localtime')"
    ).fetchone()[0]
    conn.close()
    return n

def recent(n=20):
    if USE_SUPABASE:
        r = sb.table("builds").select("*").order("id", desc=True).limit(n).execute()
        return r.data
    conn = _conn()
    rows = conn.execute(
        "SELECT id, ts, brief, style, score, zip_path "
        "FROM builds ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("archive:", "SUPABASE 🏯" if USE_SUPABASE else "local sqlite scroll")
    print("builds today:", builds_today())
    print("recent:", recent(3))
