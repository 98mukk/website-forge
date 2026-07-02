from fastapi.testclient import TestClient
from web import app

client = TestClient(app)

def test_gate_opens():
    """The homepage loads and shows the Forge."""
    r = client.get("/")
    assert r.status_code == 200
    assert "Website" in r.text

def test_memory_recalls():
    """The deck returns design intel for a query."""
    from memory import recall
    intel = recall("minimal premium design rules")
    assert len(intel) > 50
