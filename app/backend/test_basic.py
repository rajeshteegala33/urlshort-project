import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_login_shorten():
    # Signup
    r = client.post("/signup", json={"username":"testuser","password":"testpass"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # Login
    r = client.post("/login", json={"username":"testuser","password":"testpass"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Create short
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post("/shorten", json={"original_url":"https://example.com"}, headers=headers)
    assert r.status_code == 200
    short = r.json()["short"]

    # Redirect (public)
    r = client.get(f"/{short}", allow_redirects=False)
    assert r.status_code in (302, 307, 308)

    # Analytics (owner)
    r = client.get(f"/analytics/{short}", headers=headers)
    assert r.status_code == 200
    assert "total_clicks" in r.json()
