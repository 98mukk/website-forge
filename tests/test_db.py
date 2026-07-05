"""The ledger and the gate guard: db.py round-trip and guards.py daily cap."""
import pytest

db = pytest.importorskip("db", reason="db.py not written yet (contract module)")

def _use_tmp_db(tmp_path, monkeypatch):
    """Point db at a throwaway sqlite file, whatever name the path constant has."""
    monkeypatch.chdir(tmp_path)                       # covers relative-path designs
    for attr in ("DB_PATH", "DB_FILE", "PATH", "DB"):
        if isinstance(getattr(db, attr, None), str):
            monkeypatch.setattr(db, attr, str(tmp_path / "builds.db"))

def test_log_build_roundtrip(tmp_path, monkeypatch):
    _use_tmp_db(tmp_path, monkeypatch)
    assert db.builds_today() == 0
    db.log_build("a coffee shop site", "warm", 8, "static/forge-package.zip")
    db.log_build("a gym site", "bold", 6, "static/forge-package.zip")
    assert db.builds_today() == 2
    rows = db.recent()
    assert len(rows) == 2

def test_guards_cap(monkeypatch):
    guards = pytest.importorskip("guards", reason="guards.py not written yet (contract module)")

    def set_count(n):
        monkeypatch.setattr(db, "builds_today", lambda: n)
        if hasattr(guards, "builds_today"):           # in case of `from db import builds_today`
            monkeypatch.setattr(guards, "builds_today", lambda: n)

    cap = guards.MAX_BUILDS_PER_DAY
    assert cap == 25
    set_count(0)
    assert guards.allowed() is True
    set_count(cap - 1)
    assert guards.allowed() is True
    set_count(cap)
    assert guards.allowed() is False
    set_count(cap + 3)
    assert guards.allowed() is False
