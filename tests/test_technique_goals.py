"""Tests for technique goal endpoints and related features."""
from datetime import datetime, timedelta


def _technique_goal_payload(**overrides):
    data = {"position": "Butterfly Guard", "notes": "Focus on sweeps", "timeline_weeks": 4}
    data.update(overrides)
    return data


def _entry_with_technique(position, skill="Sweeps", days_ago=0):
    """Create an entry payload that includes a Class Technique response."""
    d = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    return {
        "date": d,
        "session_type": "Gi",
        "responses": [
            {"question_id": 1, "answer": "Gi"},
            {"question_id": 4, "answer": f"{position} - {skill}"},
            {"question_id": 5, "answer": "4"},
        ],
    }


# =====================
# CRUD
# =====================


class TestCreateTechniqueGoal:
    def test_create(self, client, auth_headers):
        resp = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"] == "Butterfly Guard"
        assert data["notes"] == "Focus on sweeps"
        assert data["timeline_weeks"] == 4
        assert data["is_active"] is True
        assert data["status"] == "active"

    def test_create_minimal(self, client, auth_headers):
        resp = client.post("/goals/techniques", json={"position": "Mount"}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["position"] == "Mount"
        assert data["notes"] is None
        assert data["timeline_weeks"] is None

    def test_create_unauthenticated(self, client):
        resp = client.post("/goals/techniques", json=_technique_goal_payload())
        assert resp.status_code == 401

    def test_create_multiple(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        client.post("/goals/techniques", json=_technique_goal_payload(position="Back Control"), headers=auth_headers)
        resp = client.get("/goals/techniques", headers=auth_headers)
        assert len(resp.json()) == 2


class TestGetTechniqueGoals:
    def test_get_empty(self, client, auth_headers):
        resp = client.get("/goals/techniques", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_returns_active_only(self, client, auth_headers):
        r1 = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        r2 = client.post("/goals/techniques", json=_technique_goal_payload(position="Guard"), headers=auth_headers)
        # Archive one
        client.delete(f"/goals/techniques/{r1.json()['id']}", headers=auth_headers)
        resp = client.get("/goals/techniques", headers=auth_headers)
        assert len(resp.json()) == 1
        assert resp.json()[0]["position"] == "Guard"

    def test_isolated_between_users(self, client, auth_headers, second_user_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        resp = client.get("/goals/techniques", headers=second_user_headers)
        assert len(resp.json()) == 0


class TestDeleteTechniqueGoal:
    def test_archive(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.delete(f"/goals/techniques/{goal_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Technique goal archived"
        # Should no longer appear in active list
        active = client.get("/goals/techniques", headers=auth_headers).json()
        assert len(active) == 0

    def test_archive_not_found(self, client, auth_headers):
        resp = client.delete("/goals/techniques/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_archive_other_users_goal(self, client, auth_headers, second_user_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.delete(f"/goals/techniques/{goal_id}", headers=second_user_headers)
        assert resp.status_code == 404


# =====================
# Complete / Extend
# =====================


class TestCompleteTechniqueGoal:
    def test_complete_with_rating(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "complete", "self_rating": 4},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        # No longer active
        active = client.get("/goals/techniques", headers=auth_headers).json()
        assert len(active) == 0

    def test_archive_with_rating(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "archive", "self_rating": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "archived"

    def test_extend(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(timeline_weeks=4), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "extend", "extend_weeks": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"
        # Verify timeline extended
        active = client.get("/goals/techniques", headers=auth_headers).json()
        assert active[0]["timeline_weeks"] == 6

    def test_extend_requires_weeks(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "extend"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_invalid_action(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "invalid"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_complete_not_found(self, client, auth_headers):
        resp = client.post(
            "/goals/techniques/9999/complete",
            json={"action": "complete"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_cannot_complete_other_users_goal(self, client, auth_headers, second_user_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        resp = client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "complete"},
            headers=second_user_headers,
        )
        assert resp.status_code == 404


# =====================
# Progress
# =====================


class TestTechniqueGoalProgress:
    def test_progress_empty(self, client, auth_headers):
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_progress_basic_fields(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        g = data[0]
        assert g["position"] == "Butterfly Guard"
        assert g["session_count"] == 0
        assert g["weekly_streak"] == 0
        assert "weeks_elapsed" in g
        assert "sessions_per_week" in g

    def test_progress_counts_matching_sessions(self, client, auth_headers):
        from tests.conftest import TestingSessionLocal
        from app.models import TechniqueGoal

        r = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        goal_id = r.json()["id"]
        # Backdate goal so entries from yesterday are included
        db = TestingSessionLocal()
        goal = db.query(TechniqueGoal).filter(TechniqueGoal.id == goal_id).first()
        goal.created_at = datetime.utcnow() - timedelta(days=3)
        db.commit()
        db.close()
        # Log 2 entries with Mount technique
        client.post("/entries/", json=_entry_with_technique("Mount", "Sweeps", 0), headers=auth_headers)
        client.post("/entries/", json=_entry_with_technique("Mount", "Escapes", 1), headers=auth_headers)
        # Log 1 entry with different position — should not count
        client.post("/entries/", json=_entry_with_technique("Guard", "Sweeps", 0), headers=auth_headers)
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        g = resp.json()[0]
        assert g["session_count"] == 2

    def test_progress_days_left(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(timeline_weeks=4), headers=auth_headers)
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        g = resp.json()[0]
        assert g["days_left"] is not None
        assert g["total_days"] == 28
        # Just created, so days_left should be close to 28
        assert 26 <= g["days_left"] <= 28

    def test_progress_no_timeline(self, client, auth_headers):
        client.post("/goals/techniques", json={"position": "Mount"}, headers=auth_headers)
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        g = resp.json()[0]
        assert g["days_left"] is None
        assert g["total_days"] is None

    def test_progress_weekly_streak(self, client, auth_headers):
        from tests.conftest import TestingSessionLocal
        from app.models import TechniqueGoal

        r = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        goal_id = r.json()["id"]
        # Backdate goal by 2 weeks so entries from last week are within scope
        db = TestingSessionLocal()
        goal = db.query(TechniqueGoal).filter(TechniqueGoal.id == goal_id).first()
        goal.created_at = datetime.utcnow() - timedelta(days=14)
        db.commit()
        db.close()
        # Log entries in current week and last week
        client.post("/entries/", json=_entry_with_technique("Mount", "Sweeps", 0), headers=auth_headers)
        client.post("/entries/", json=_entry_with_technique("Mount", "Escapes", 7), headers=auth_headers)
        resp = client.get("/goals/techniques/progress", headers=auth_headers)
        g = resp.json()[0]
        # Should have at least 1 week streak (current week)
        assert g["weekly_streak"] >= 1


# =====================
# Expired
# =====================


class TestExpiredTechniqueGoals:
    def test_expired_empty(self, client, auth_headers):
        resp = client.get("/goals/techniques/expired", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_not_expired_yet(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(timeline_weeks=4), headers=auth_headers)
        resp = client.get("/goals/techniques/expired", headers=auth_headers)
        assert resp.json() == []

    def test_no_timeline_never_expires(self, client, auth_headers):
        client.post("/goals/techniques", json={"position": "Mount"}, headers=auth_headers)
        resp = client.get("/goals/techniques/expired", headers=auth_headers)
        assert resp.json() == []

    def test_expired_goal_detected(self, client, auth_headers):
        """Create a goal and manually backdate it so it's expired."""
        from tests.conftest import TestingSessionLocal
        from app.models import TechniqueGoal

        r = client.post("/goals/techniques", json=_technique_goal_payload(timeline_weeks=1), headers=auth_headers)
        goal_id = r.json()["id"]
        # Backdate created_at by 2 weeks so the 1-week goal is expired
        db = TestingSessionLocal()
        goal = db.query(TechniqueGoal).filter(TechniqueGoal.id == goal_id).first()
        goal.created_at = datetime.utcnow() - timedelta(weeks=2)
        db.commit()
        db.close()

        resp = client.get("/goals/techniques/expired", headers=auth_headers)
        data = resp.json()
        assert len(data) == 1
        assert data[0]["position"] == "Butterfly Guard"
        assert data[0]["days_overdue"] >= 7


# =====================
# History
# =====================


class TestTechniqueGoalHistory:
    def test_history_empty(self, client, auth_headers):
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_active_goals_not_in_history(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        assert resp.json() == []

    def test_completed_goal_in_history(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "complete", "self_rating": 5},
            headers=auth_headers,
        )
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"
        assert data[0]["self_rating"] == 5
        assert data[0]["position"] == "Butterfly Guard"
        assert data[0]["completed_at"] is not None

    def test_archived_goal_in_history(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        goal_id = r.json()["id"]
        client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "archive", "self_rating": 3},
            headers=auth_headers,
        )
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "archived"
        assert data[0]["self_rating"] == 3

    def test_history_includes_session_count(self, client, auth_headers):
        # Log an entry with Mount technique
        client.post("/entries/", json=_entry_with_technique("Mount", "Sweeps", 0), headers=auth_headers)
        # Create and complete a goal for Mount
        r = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        goal_id = r.json()["id"]
        # Log another entry after goal creation
        client.post("/entries/", json=_entry_with_technique("Mount", "Escapes", 0), headers=auth_headers)
        client.post(
            f"/goals/techniques/{goal_id}/complete",
            json={"action": "complete", "self_rating": 4},
            headers=auth_headers,
        )
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        data = resp.json()
        assert len(data) == 1
        # Should count at least the entry logged after goal creation
        assert data[0]["session_count"] >= 1
        assert data[0]["duration_weeks"] >= 0

    def test_history_ordered_by_completed_at_desc(self, client, auth_headers):
        # Create and complete two goals
        r1 = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        client.post(f"/goals/techniques/{r1.json()['id']}/complete", json={"action": "complete"}, headers=auth_headers)
        r2 = client.post("/goals/techniques", json=_technique_goal_payload(position="Guard"), headers=auth_headers)
        client.post(f"/goals/techniques/{r2.json()['id']}/complete", json={"action": "complete"}, headers=auth_headers)
        resp = client.get("/goals/techniques/history", headers=auth_headers)
        data = resp.json()
        assert len(data) == 2
        # Most recently completed should be first
        assert data[0]["position"] == "Guard"
        assert data[1]["position"] == "Mount"

    def test_history_isolated_between_users(self, client, auth_headers, second_user_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(), headers=auth_headers)
        client.post(f"/goals/techniques/{r.json()['id']}/complete", json={"action": "complete"}, headers=auth_headers)
        resp = client.get("/goals/techniques/history", headers=second_user_headers)
        assert resp.json() == []


# =====================
# Recommendations integration
# =====================


class TestTechniqueGoalRecommendations:
    def test_no_recs_without_goals(self, client, auth_headers):
        resp = client.get("/recommendations/", headers=auth_headers)
        assert resp.status_code == 200
        recs = resp.json()["recommendations"]
        tg_recs = [r for r in recs if r["type"] == "technique_goal"]
        assert len(tg_recs) == 0

    def test_rec_fires_for_untrained_goal(self, client, auth_headers):
        client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        resp = client.get("/recommendations/", headers=auth_headers)
        recs = resp.json()["recommendations"]
        tg_recs = [r for r in recs if r["type"] == "technique_goal"]
        assert len(tg_recs) == 1
        assert tg_recs[0]["priority"] == "high"
        assert "Mount" in tg_recs[0]["title"]

    def test_no_rec_for_archived_goal(self, client, auth_headers):
        r = client.post("/goals/techniques", json=_technique_goal_payload(position="Mount"), headers=auth_headers)
        client.delete(f"/goals/techniques/{r.json()['id']}", headers=auth_headers)
        resp = client.get("/recommendations/", headers=auth_headers)
        recs = resp.json()["recommendations"]
        tg_recs = [r for r in recs if r["type"] == "technique_goal"]
        assert len(tg_recs) == 0
