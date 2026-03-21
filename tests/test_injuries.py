"""Tests for injury endpoints."""
from datetime import date


def _injury_payload(**overrides):
    data = {
        "injured_area": "Knee",
        "injury_date": date.today().isoformat(),
        "cause": "Takedown",
        "notes": "Mild sprain",
    }
    data.update(overrides)
    return data


class TestCreateInjury:
    def test_create_injury(self, client, auth_headers):
        resp = client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["injured_area"] == "Knee"
        assert resp.json()["end_date"] is None

    def test_create_injury_unauthenticated(self, client):
        resp = client.post("/injuries/", json=_injury_payload())
        assert resp.status_code == 401


class TestGetInjuries:
    def test_get_all_injuries(self, client, auth_headers):
        client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        client.post("/injuries/", json=_injury_payload(injured_area="Shoulder"), headers=auth_headers)
        resp = client.get("/injuries/", headers=auth_headers)
        assert len(resp.json()) == 2

    def test_get_active_injuries(self, client, auth_headers):
        # Active injury (no end_date)
        client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        # Healed injury
        client.post("/injuries/", json=_injury_payload(
            injured_area="Elbow", end_date=date.today().isoformat()
        ), headers=auth_headers)
        resp = client.get("/injuries/active", headers=auth_headers)
        assert len(resp.json()) == 1
        assert resp.json()[0]["injured_area"] == "Knee"

    def test_injuries_isolated_between_users(self, client, auth_headers, second_user_headers):
        client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        resp = client.get("/injuries/", headers=second_user_headers)
        assert len(resp.json()) == 0


class TestGetSingleInjury:
    def test_get_injury_by_id(self, client, auth_headers):
        create_resp = client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        injury_id = create_resp.json()["id"]
        resp = client.get(f"/injuries/{injury_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_get_injury_not_found(self, client, auth_headers):
        resp = client.get("/injuries/9999", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateInjury:
    def test_update_injury(self, client, auth_headers):
        create_resp = client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        injury_id = create_resp.json()["id"]
        resp = client.put(f"/injuries/{injury_id}", json=_injury_payload(
            injured_area="Shoulder", end_date=date.today().isoformat()
        ), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["injured_area"] == "Shoulder"
        assert resp.json()["end_date"] is not None

    def test_update_nonexistent(self, client, auth_headers):
        resp = client.put("/injuries/9999", json=_injury_payload(), headers=auth_headers)
        assert resp.status_code == 404


class TestDeleteInjury:
    def test_delete_injury(self, client, auth_headers):
        create_resp = client.post("/injuries/", json=_injury_payload(), headers=auth_headers)
        injury_id = create_resp.json()["id"]
        resp = client.delete(f"/injuries/{injury_id}", headers=auth_headers)
        assert resp.status_code == 200
        resp = client.get(f"/injuries/{injury_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/injuries/9999", headers=auth_headers)
        assert resp.status_code == 404
