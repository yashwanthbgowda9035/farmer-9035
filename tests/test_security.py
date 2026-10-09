def test_security_headers_present(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "microphone=(self)" in response.headers.get("Permissions-Policy", "")

def test_accessibility_skip_link_present(client):
    response = client.get("/")
    assert b"skip-to-content" in response.data
    assert b"Skip to primary content" in response.data
    assert b"role=\"main\"" in response.data

def test_rate_limiter_protection(auth_client):
    # Send repeated requests to test rate limit (limit is 15/min)
    res = None
    for _ in range(20):
        res = auth_client.post("/agent/chat", json={"query": "test query", "language": "en"})
    
    # After 15+ requests within 60s, rate limiter triggers 429
    assert res.status_code == 429
    assert res.json["status"] == "rate_limited"

def test_static_cache_control_headers(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "max-age" in response.headers.get("Cache-Control", "")
