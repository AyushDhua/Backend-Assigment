def test_register_success(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert res.status_code == 201
    assert "access_token" in res.get_json()["data"]

def test_register_duplicate_email(client):
    client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    res = client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert res.status_code == 400
    assert "already exists" in res.get_json()["message"].lower()

def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert res.status_code == 200
    assert "access_token" in res.get_json()["data"]

def test_login_invalid_credentials(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert "invalid" in res.get_json()["message"].lower()
