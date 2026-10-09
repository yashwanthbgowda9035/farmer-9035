def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"KrishiMitra AI" in response.data

def test_protected_routes_redirect_unauth(client):
    protected_urls = [
        "/dashboard",
        "/crop/detect",
        "/agent/assistant",
        "/knowledge/",
        "/weather/",
        "/recommendations/",
        "/soil/",
        "/irrigation/",
        "/monitoring/",
        "/market/",
        "/market/yield",
        "/alerts"
    ]
    for url in protected_urls:
        res = client.get(url)
        assert res.status_code in [302, 401]

def test_authenticated_routes_load(auth_client):
    routes = [
        "/dashboard",
        "/crop/detect",
        "/agent/assistant",
        "/knowledge/",
        "/weather/",
        "/recommendations/",
        "/soil/",
        "/irrigation/",
        "/monitoring/",
        "/market/",
        "/market/yield",
        "/alerts",
        "/settings"
    ]
    for r in routes:
        res = auth_client.get(r)
        assert res.status_code == 200, f"Route {r} failed with status {res.status_code}"
