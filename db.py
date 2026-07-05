"""The Ledger: every build logged to sqlite. No ORM, no ceremony."""
import sqlite3

DB_PATH = "builds.db"

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS builds("
        "id INTEGER PRIMARY KEY, ts TEXT, brief TEXT, style TEXT, "
        "score INTEGER, zip_path TEXT)"
    )
    return conn

def log_build(brief, style, score, zip_path):
    conn = _conn()
    conn.execute(
        "INSERT INTO builds(ts, brief, style, score, zip_path) "
        "VALUES (datetime('now','localtime'), ?, ?, ?, ?)",
        (brief, style, score, zip_path),
    )
    conn.commit()
    conn.close()

def builds_today():
    conn = _conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM builds WHERE date(ts) = date('now','localtime')"
    ).fetchone()[0]
    conn.close()
    return n

def recent(n=20):
    conn = _conn()
    rows = conn.execute(
        "SELECT id, ts, brief, style, score, zip_path "
        "FROM builds ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return rows
