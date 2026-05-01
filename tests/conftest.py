import pytest
from backend.app import create_app
from backend.extensions import db

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
