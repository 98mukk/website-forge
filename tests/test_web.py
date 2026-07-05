"""The gates: / serves the Forge, /status honors the contract. No API calls."""

def test_gate_opens(client):
    """The homepage loads and shows the Forge."""
    r = client.get("/")
    assert r.status_code == 200
    assert "Website" in r.text

def test_status_contract(client):
    """/status returns the full contract shape."""
    r = client.get("/status")
    assert r.status_code == 200
    s = r.json()
    for key in ("stage", "log", "done", "error", "score", "package", "kit"):
        assert key in s, f"missing key: {key}"
    assert isinstance(s["stage"], str)
    assert isinstance(s["log"], list)
    assert isinstance(s["done"], bool)
    assert s["error"] is None or isinstance(s["error"], str)
    assert s["score"] is None or isinstance(s["score"], int)
    assert s["package"] in (None, "/static/forge-package.zip")
    assert s["kit"] in (None, "/static/kit.html")

def test_memory_recalls(client):
    """The deck returns design intel for a query."""
    from memory import recall
    intel = recall("minimal premium design rules")
    assert len(intel) > 50
