def test_user_registration(client):
    res = client.post("/api/v1/register", json={"email": "user@example.com", "password": "Password123!"})
    assert res.status_code == 201
    assert res.json()["email"] == "user@example.com"
    assert res.json()["role"] == "MANAGER"

def test_login_success(client):
    client.post("/api/v1/register", json={"email": "user@example.com", "password": "Password123!"})
    res = client.post("/api/v1/login", data={"username": "user@example.com", "password": "Password123!"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_invalid_password(client):
    client.post("/api/v1/register", json={"email": "user@example.com", "password": "Password123!"})
    res = client.post("/api/v1/login", data={"username": "user@example.com", "password": "WrongPassword123!"})
    assert res.status_code == 401

def test_read_users_me(client, auth_headers):
    res = client.get("/api/v1/users/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "developer@example.com"
