def test_farmer_cannot_access_admin(auth_client):
    response = auth_client.get("/admin/")
    assert response.status_code == 403

def test_admin_can_access_admin(admin_client):
    response = admin_client.get("/admin/")
    assert response.status_code == 200
    assert b"Administrator System Dashboard" in response.data

def test_non_admin_cannot_import_knowledge(auth_client):
    response = auth_client.post("/knowledge/import", data={
        "title": "Malicious Doc",
        "author": "Attacker"
    }, follow_redirects=True)
    assert b"Unauthorized. Only administrators" in response.data
