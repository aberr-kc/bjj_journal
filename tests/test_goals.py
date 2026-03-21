"""Tests for goals and streak endpoints."""
from datetime import date, datetime


def _goal_payload(**overrides):
    data = {
        "weekly_sessions_target": 3,
        "weekly_rounds_target": 10,
        "start_date": date.today().isoformat(),
    }
    data.update(overrides)
    return data


def _entry_payload():
    return {
        "date": datetime.utcnow().isoformat(),
        "session_type": "Gi",
        "responses": [
            {"question_id": 1, "answer": "Gi"},
            {"question_id": 2, "answer": "6"},
            {"question_id": 5, "answer": "4"},
        ]
    }


class TestCreateGoal:
    def test_create_goal(self, client, auth_headers):
        resp = client.post("/goals/", json=_goal_payload(), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["weekly_sessions_target"] == 3
        assert resp.json()["is_active"] is True

    def test_create_goal_deactivates_previous(self, client, auth_headers):
        client.post("/goals/", json=_goal_payload(), headers=auth_headers)
        client.post("/goals/", json=_goal_payload(weekly_sessions_target=5), headers=auth_headers)
        resp = client.get("/goals/current", headers=auth_headers)
        assert resp.json()["weekly_sessions_target"] == 5

    def test_create_goal_unauthenticated(self, client):
        resp = client.post("/goals/", json=_goal_payload())
        assert resp.status_code == 401


class TestGetGoal:
    def test_get_current_goal(self, client, auth_headers):
        client.post("/goals/", json=_goal_payload(), headers=auth_headers)
        resp = client.get("/goals/current", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["weekly_sessions_target"] == 3

    def test_get_current_goal_none(self, client, auth_headers):
        resp = client.get("/goals/current", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() is None

    def test_get_goal_history(self, client, auth_headers):
        client.post("/goals/", json=_goal_payload(), headers=auth_headers)
        client.post("/goals/", json=_goal_payload(weekly_sessions_target=5), headers=auth_headers)
        resp = client.get("/goals/history", headers=auth_headers)
        assert len(resp.json()) == 2


class TestStreaks:
    def test_get_streak_no_goal(self, client, auth_headers):
        resp = client.get("/goals/streaks/current", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["current_streak"] == 0
        assert resp.json()["current_week_goal"] == 0

    def test_get_streak_with_goal(self, client, auth_headers):
        client.post("/goals/", json=_goal_payload(), headers=auth_headers)
        resp = client.get("/goals/streaks/current", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["current_week_goal"] == 3

    def test_streak_tracks_sessions(self, client, auth_headers):
        client.post("/goals/", json=_goal_payload(weekly_sessions_target=1), headers=auth_headers)
        client.post("/entries/", json=_entry_payload(), headers=auth_headers)
        resp = client.get("/goals/streaks/current", headers=auth_headers)
        assert resp.json()["current_week_progress"] >= 1


class TestQuestions:
    def test_get_questions(self, client):
        resp = client.get("/questions/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
        assert resp.json()[0]["question_text"] == "Session Type"
