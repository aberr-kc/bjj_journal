"""Tests for analytics/dashboard endpoint."""
from datetime import datetime


def _entry_payload(session_type="Gi", rpe="6", rounds="5", technique="Mount - Escapes"):
    return {
        "date": datetime.utcnow().isoformat(),
        "session_type": session_type,
        "responses": [
            {"question_id": 1, "answer": session_type},
            {"question_id": 2, "answer": rpe},
            {"question_id": 3, "answer": "Class"},
            {"question_id": 4, "answer": technique},
            {"question_id": 5, "answer": rounds},
        ]
    }


class TestDashboard:
    def test_dashboard_empty(self, client, auth_headers):
        resp = client.get("/analytics/dashboard", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 0
        assert data["avg_rpe"] == 0

    def test_dashboard_with_entries(self, client, auth_headers):
        client.post("/entries/", json=_entry_payload(), headers=auth_headers)
        client.post("/entries/", json=_entry_payload("No Gi", "8", "3"), headers=auth_headers)
        resp = client.get("/analytics/dashboard", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_sessions"] == 2
        assert data["total_rounds"] == 8
        assert data["avg_rpe"] == 7.0

    def test_dashboard_period_filter(self, client, auth_headers):
        client.post("/entries/", json=_entry_payload(), headers=auth_headers)
        resp = client.get("/analytics/dashboard?period=7d", headers=auth_headers)
        assert resp.status_code == 200
        resp = client.get("/analytics/dashboard?period=all", headers=auth_headers)
        assert resp.status_code == 200

    def test_dashboard_unauthenticated(self, client):
        resp = client.get("/analytics/dashboard")
        assert resp.status_code == 401

    def test_dashboard_session_types(self, client, auth_headers):
        client.post("/entries/", json=_entry_payload("Gi"), headers=auth_headers)
        client.post("/entries/", json=_entry_payload("Gi"), headers=auth_headers)
        client.post("/entries/", json=_entry_payload("No Gi"), headers=auth_headers)
        resp = client.get("/analytics/dashboard?period=all", headers=auth_headers)
        data = resp.json()
        assert data["session_types"].get("Gi") == 2
        assert data["session_types"].get("No Gi") == 1

    def test_dashboard_isolated_between_users(self, client, auth_headers, second_user_headers):
        client.post("/entries/", json=_entry_payload(), headers=auth_headers)
        resp = client.get("/analytics/dashboard", headers=second_user_headers)
        assert resp.json()["total_sessions"] == 0
