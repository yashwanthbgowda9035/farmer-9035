import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from app import create_app
from config import TestConfig
from models.database import db
from models.user import User

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Create test users
        admin = User(username="test_admin", email="admin@test.com", role="admin")
        admin.set_password("AdminPass123!")
        farmer = User(username="test_farmer", email="farmer@test.com", role="farmer")
        farmer.set_password("FarmerPass123!")
        db.session.add_all([admin, farmer])
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    # Log in as test farmer
    client.post("/auth/login", data={"username": "test_farmer", "password": "FarmerPass123!"})
    return client

@pytest.fixture
def admin_client(client):
    # Log in as test admin
    client.post("/auth/login", data={"username": "test_admin", "password": "AdminPass123!"})
    return client
