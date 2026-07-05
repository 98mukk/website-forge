"""Shared fixtures. Importing web boots the chroma deck (~10s), so do it once per session."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

@pytest.fixture(scope="session")
def client():
    os.chdir(ROOT)                     # chroma + templates use relative paths
    from fastapi.testclient import TestClient
    import web
    return TestClient(web.app)
