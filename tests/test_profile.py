"""Tests for profile endpoints."""


def _profile_payload(**overrides):
    data = {"name": "Test User", "age": 30, "weight": 80.0, "height": 180.0, "belt": "Blue"}
    data.update(overrides)
    return data


class TestProfile:
    def test_get_profile_not_found(self, client, auth_headers):
        resp = client.get("/profile/", headers=auth_headers)
        assert resp.status_code == 404

    def test_create_profile(self, client, auth_headers):
        resp = client.post("/profile/", json=_profile_payload(), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test User"
        assert resp.json()["belt"] == "Blue"

    def test_create_duplicate_profile(self, client, auth_headers):
        client.post("/profile/", json=_profile_payload(), headers=auth_headers)
        resp = client.post("/profile/", json=_profile_payload(), headers=auth_headers)
        assert resp.status_code == 400

    def test_update_profile(self, client, auth_headers):
        client.post("/profile/", json=_profile_payload(), headers=auth_headers)
        resp = client.put("/profile/", json=_profile_payload(belt="Purple", weight=85.0), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["belt"] == "Purple"
        assert resp.json()["weight"] == 85.0

    def test_update_creates_if_missing(self, client, auth_headers):
        resp = client.put("/profile/", json=_profile_payload(), headers=auth_headers)
        assert resp.status_code == 200

    def test_profile_exists_false(self, client, auth_headers):
        resp = client.get("/profile/exists", headers=auth_headers)
        assert resp.json()["exists"] is False

    def test_profile_exists_true(self, client, auth_headers):
        client.post("/profile/", json=_profile_payload(), headers=auth_headers)
        resp = client.get("/profile/exists", headers=auth_headers)
        assert resp.json()["exists"] is True

    def test_profile_unauthenticated(self, client):
        resp = client.get("/profile/")
        assert resp.status_code == 401
