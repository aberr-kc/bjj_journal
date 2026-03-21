"""Tests for entry CRUD endpoints."""
from datetime import datetime


def _make_entry_payload(session_type="Gi"):
    return {
        "date": datetime.utcnow().isoformat(),
        "session_type": session_type,
        "responses": [
            {"question_id": 1, "answer": "Gi"},
            {"question_id": 2, "answer": "7"},
            {"question_id": 5, "answer": "5"},
        ]
    }


class TestCreateEntry:
    def test_create_entry(self, client, auth_headers):
        resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_type"] == "Gi"
        assert len(data["responses"]) == 3

    def test_create_entry_unauthenticated(self, client):
        resp = client.post("/entries/", json=_make_entry_payload())
        assert resp.status_code == 401


class TestGetEntries:
    def test_get_entries_empty(self, client, auth_headers):
        resp = client.get("/entries/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_entries_returns_own(self, client, auth_headers):
        client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        client.post("/entries/", json=_make_entry_payload("No Gi"), headers=auth_headers)
        resp = client.get("/entries/", headers=auth_headers)
        assert len(resp.json()) == 2

    def test_entries_isolated_between_users(self, client, auth_headers, second_user_headers):
        client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        resp = client.get("/entries/", headers=second_user_headers)
        assert len(resp.json()) == 0


class TestGetSingleEntry:
    def test_get_entry_by_id(self, client, auth_headers):
        create_resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        entry_id = create_resp.json()["id"]
        resp = client.get(f"/entries/{entry_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == entry_id

    def test_get_entry_not_found(self, client, auth_headers):
        resp = client.get("/entries/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_get_other_users_entry(self, client, auth_headers, second_user_headers):
        create_resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        entry_id = create_resp.json()["id"]
        resp = client.get(f"/entries/{entry_id}", headers=second_user_headers)
        assert resp.status_code == 404


class TestUpdateEntry:
    def test_update_entry(self, client, auth_headers):
        create_resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        entry_id = create_resp.json()["id"]
        updated = _make_entry_payload("No Gi")
        resp = client.put(f"/entries/{entry_id}", json=updated, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["session_type"] == "No Gi"

    def test_update_nonexistent_entry(self, client, auth_headers):
        resp = client.put("/entries/9999", json=_make_entry_payload(), headers=auth_headers)
        assert resp.status_code == 404


class TestDeleteEntry:
    def test_delete_entry(self, client, auth_headers):
        create_resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        entry_id = create_resp.json()["id"]
        resp = client.delete(f"/entries/{entry_id}", headers=auth_headers)
        assert resp.status_code == 200
        # Verify deleted
        resp = client.get(f"/entries/{entry_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_entry(self, client, auth_headers):
        resp = client.delete("/entries/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_delete_other_users_entry(self, client, auth_headers, second_user_headers):
        create_resp = client.post("/entries/", json=_make_entry_payload(), headers=auth_headers)
        entry_id = create_resp.json()["id"]
        resp = client.delete(f"/entries/{entry_id}", headers=second_user_headers)
        assert resp.status_code == 404
