"""Tests for authentication endpoints."""


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={"username": "newuser", "password": "pass123"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "User created successfully"

    def test_register_duplicate_username(self, client):
        client.post("/auth/register", json={"username": "dup", "password": "pass"})
        resp = client.post("/auth/register", json={"username": "dup", "password": "pass"})
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]


class TestLogin:
    def test_login_success(self, client):
        client.post("/auth/register", json={"username": "loginuser", "password": "pass"})
        resp = client.post("/auth/login", json={"username": "loginuser", "password": "pass"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/auth/register", json={"username": "user1", "password": "correct"})
        resp = client.post("/auth/login", json={"username": "user1", "password": "wrong"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/auth/login", json={"username": "ghost", "password": "pass"})
        assert resp.status_code == 401


class TestChangePassword:
    def test_change_password_success(self, client, auth_headers):
        resp = client.put("/auth/change-password", json={
            "old_password": "testpass", "new_password": "newpass"
        }, headers=auth_headers)
        assert resp.status_code == 200

        # Login with new password
        resp = client.post("/auth/login", json={"username": "testuser", "password": "newpass"})
        assert resp.status_code == 200

    def test_change_password_wrong_old(self, client, auth_headers):
        resp = client.put("/auth/change-password", json={
            "old_password": "wrongold", "new_password": "newpass"
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_change_password_unauthenticated(self, client):
        resp = client.put("/auth/change-password", json={
            "old_password": "a", "new_password": "b"
        })
        assert resp.status_code == 401
