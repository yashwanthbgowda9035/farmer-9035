def test_register_success(client):
    response = client.post("/auth/register", data={
        "username": "new_farmer",
        "email": "new@farmer.com",
        "password": "Password123!",
        "preferred_language": "en",
        "location": "Kolar, Karnataka"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data or b"Dashboard" in response.data

def test_register_duplicate_username(client):
    response = client.post("/auth/register", data={
        "username": "test_farmer",
        "email": "diff@farmer.com",
        "password": "Password123!"
    }, follow_redirects=True)
    assert b"Username already taken" in response.data

def test_login_success(client):
    response = client.post("/auth/login", data={
        "username": "test_farmer",
        "password": "FarmerPass123!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back, test_farmer" in response.data or b"Namaskara" in response.data

def test_login_invalid_password(client):
    response = client.post("/auth/login", data={
        "username": "test_farmer",
        "password": "WrongPassword!"
    }, follow_redirects=True)
    assert b"Invalid username/email or password" in response.data

def test_logout(auth_client):
    response = auth_client.get("/auth/logout", follow_redirects=True)
    assert b"signed out" in response.data or b"Sign In" in response.data
