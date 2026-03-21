"""Unit tests for the recommendation engine logic."""
import pytest
from datetime import datetime, timedelta
from app.routers.recommendations import (
    check_data_gates,
    get_stale_window_days,
    recommend_positions,
    recommend_submissions,
    recommend_intensity,
    extract_rpe_values,
    extract_technique_data,
)


# --- Helpers to build fake data ---

def make_entry(date, id_=1):
    """Create a minimal entry-like object."""
    class FakeEntry:
        pass
    e = FakeEntry()
    e.id = id_
    e.date = date
    e.session_type = "Gi"
    return e


def make_response(entry_id, question_text, answer, entry=None):
    """Create a minimal response-like object."""
    class FakeQuestion:
        pass
    class FakeResponse:
        pass
    q = FakeQuestion()
    q.question_text = question_text
    r = FakeResponse()
    r.entry_id = entry_id
    r.question = q
    r.answer = answer
    r.entry = entry
    return r


def make_technique_data(position_counts=None, skill_counts=None,
                        position_last_seen=None, position_skills=None):
    return {
        "position_counts": position_counts or {},
        "skill_counts": skill_counts or {},
        "position_last_seen": position_last_seen or {},
        "position_skills": position_skills or {},
    }


# =====================
# Phase 1: Data Gates
# =====================

class TestDataGates:
    def test_all_gates_fail_with_no_data(self):
        td = make_technique_data()
        gates = check_data_gates(0, td, [], [])
        assert gates["position"] is False
        assert gates["submission"] is False
        assert gates["intensity"] is False

    def test_position_gate_requires_10_sessions_and_3_positions(self):
        td = make_technique_data(position_counts={"Mount": 4, "Guard": 3, "Back": 3})
        entries = [make_entry(datetime.utcnow(), i) for i in range(10)]
        gates = check_data_gates(10, td, [], entries)
        assert gates["position"] is True

    def test_position_gate_fails_with_few_positions(self):
        td = make_technique_data(position_counts={"Mount": 8, "Guard": 2})
        entries = [make_entry(datetime.utcnow(), i) for i in range(10)]
        gates = check_data_gates(10, td, [], entries)
        assert gates["position"] is False

    def test_position_gate_fails_with_few_sessions(self):
        td = make_technique_data(position_counts={"Mount": 3, "Guard": 3, "Back": 3})
        entries = [make_entry(datetime.utcnow(), i) for i in range(9)]
        gates = check_data_gates(9, td, [], entries)
        assert gates["position"] is False

    def test_submission_gate_requires_submissions_exist(self):
        td = make_technique_data(skill_counts={"Attacks/Submissions": 2})
        gates = check_data_gates(10, td, [], [])
        assert gates["submission"] is True

    def test_submission_gate_fails_without_submissions(self):
        td = make_technique_data(skill_counts={"Sweeps": 5})
        gates = check_data_gates(10, td, [], [])
        assert gates["submission"] is False

    def test_intensity_gate_requires_5_recent_sessions(self):
        now = datetime.utcnow()
        entries = [make_entry(now - timedelta(days=i), i) for i in range(5)]
        td = make_technique_data()
        gates = check_data_gates(5, td, [], entries)
        assert gates["intensity"] is True

    def test_intensity_gate_fails_with_old_sessions(self):
        now = datetime.utcnow()
        entries = [make_entry(now - timedelta(days=30 + i), i) for i in range(10)]
        td = make_technique_data()
        gates = check_data_gates(10, td, [], entries)
        assert gates["intensity"] is False


# =====================
# Phase 3: Adaptive Stale Window
# =====================

class TestStaleWindow:
    def test_high_frequency_gets_short_window(self):
        now = datetime.utcnow()
        # 5+ sessions per week over 60 days = ~40+ sessions
        entries = [make_entry(now - timedelta(days=i), i) for i in range(45)]
        assert get_stale_window_days(entries) == 21

    def test_medium_frequency_gets_default_window(self):
        now = datetime.utcnow()
        # ~3.5 sessions per week
        entries = [make_entry(now - timedelta(days=i*2), i) for i in range(30)]
        assert get_stale_window_days(entries) == 30

    def test_low_frequency_gets_long_window(self):
        now = datetime.utcnow()
        # ~1 session per week
        entries = [make_entry(now - timedelta(days=i*7), i) for i in range(8)]
        assert get_stale_window_days(entries) == 45

    def test_no_entries_gets_long_window(self):
        assert get_stale_window_days([]) == 45


# =====================
# Position Recommendations
# =====================

class TestPositionRecommendations:
    def test_stale_position_fires_when_trained_3_plus_times(self):
        now = datetime.utcnow()
        td = make_technique_data(
            position_counts={"Mount": 5},
            position_last_seen={"Mount": now - timedelta(days=35)},
            position_skills={"Mount": {"Escapes": 3, "Sweeps": 2}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        assert len(recs) == 1
        assert recs[0]["title"] == "Revisit Mount"

    def test_stale_position_ignored_if_trained_less_than_3_times(self):
        now = datetime.utcnow()
        td = make_technique_data(
            position_counts={"Mount": 2},
            position_last_seen={"Mount": now - timedelta(days=40)},
            position_skills={"Mount": {"Escapes": 2}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        stale_recs = [r for r in recs if "Revisit" in r["title"]]
        assert len(stale_recs) == 0

    def test_stale_position_not_fired_if_recent(self):
        now = datetime.utcnow()
        td = make_technique_data(
            position_counts={"Mount": 5},
            position_last_seen={"Mount": now - timedelta(days=10)},
            position_skills={"Mount": {"Escapes": 3, "Sweeps": 2}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        stale_recs = [r for r in recs if "Revisit" in r["title"]]
        assert len(stale_recs) == 0

    def test_limited_skill_diversity_fires_at_5_sessions(self):
        td = make_technique_data(
            position_counts={"Mount": 5},
            position_last_seen={"Mount": datetime.utcnow()},
            position_skills={"Mount": {"Escapes": 5}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        diversity_recs = [r for r in recs if "Expand" in r["title"]]
        assert len(diversity_recs) == 1

    def test_limited_skill_diversity_does_not_fire_at_4_sessions(self):
        td = make_technique_data(
            position_counts={"Mount": 4},
            position_last_seen={"Mount": datetime.utcnow()},
            position_skills={"Mount": {"Escapes": 4}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        diversity_recs = [r for r in recs if "Expand" in r["title"]]
        assert len(diversity_recs) == 0

    def test_no_guard_passing_fires(self):
        td = make_technique_data(
            position_counts={"Closed Guard": 3, "Half Guard": 3},
            position_last_seen={"Closed Guard": datetime.utcnow(), "Half Guard": datetime.utcnow()},
            position_skills={"Closed Guard": {"Sweeps": 3}, "Half Guard": {"Escapes": 3}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        passing_recs = [r for r in recs if "guard passing" in r["title"].lower()]
        assert len(passing_recs) == 1
        assert passing_recs[0]["priority"] == "high"

    def test_guard_passing_imbalance_fires(self):
        td = make_technique_data(
            position_counts={"Closed Guard": 8, "Guard Passing": 1},
            position_last_seen={"Closed Guard": datetime.utcnow(), "Guard Passing": datetime.utcnow()},
            position_skills={"Closed Guard": {"Sweeps": 8}, "Guard Passing": {"Pressure": 1}},
        )
        recs = recommend_positions(td, [], stale_days=30)
        imbalance_recs = [r for r in recs if "imbalance" in r["title"].lower()]
        assert len(imbalance_recs) == 1


# =====================
# Submission Recommendations
# =====================

class TestSubmissionRecommendations:
    def test_low_frequency_fires_at_15_sessions(self):
        td = make_technique_data(
            skill_counts={"Attacks/Submissions": 2, "Sweeps": 10, "Escapes": 3},
            position_skills={"Mount": {"Sweeps": 10}, "Guard": {"Escapes": 3}, "Back": {"Attacks/Submissions": 2}},
        )
        recs = recommend_submissions(td, total_sessions=15)
        assert len(recs) >= 1
        assert recs[0]["title"] == "Increase submission focus"

    def test_low_frequency_does_not_fire_at_14_sessions(self):
        td = make_technique_data(
            skill_counts={"Attacks/Submissions": 2, "Sweeps": 10},
            position_skills={},
        )
        recs = recommend_submissions(td, total_sessions=14)
        freq_recs = [r for r in recs if "Increase" in r["title"]]
        assert len(freq_recs) == 0

    def test_low_frequency_does_not_fire_when_above_20_percent(self):
        td = make_technique_data(
            skill_counts={"Attacks/Submissions": 5, "Sweeps": 10},
            position_skills={},
        )
        recs = recommend_submissions(td, total_sessions=15)
        freq_recs = [r for r in recs if "Increase" in r["title"]]
        assert len(freq_recs) == 0

    def test_no_submissions_from_position_fires_at_6(self):
        td = make_technique_data(
            skill_counts={"Sweeps": 6},
            position_skills={"Mount": {"Sweeps": 6}},
            position_counts={"Mount": 6},
        )
        recs = recommend_submissions(td, total_sessions=20)
        pos_recs = [r for r in recs if "Add submissions" in r["title"]]
        assert len(pos_recs) == 1

    def test_no_submissions_from_position_does_not_fire_at_5(self):
        td = make_technique_data(
            skill_counts={"Sweeps": 5},
            position_skills={"Mount": {"Sweeps": 5}},
            position_counts={"Mount": 5},
        )
        recs = recommend_submissions(td, total_sessions=20)
        pos_recs = [r for r in recs if "Add submissions" in r["title"]]
        assert len(pos_recs) == 0

    def test_clears_when_submission_logged(self):
        td = make_technique_data(
            skill_counts={"Sweeps": 5, "Attacks/Submissions": 1},
            position_skills={"Mount": {"Sweeps": 5, "Attacks/Submissions": 1}},
            position_counts={"Mount": 6},
        )
        recs = recommend_submissions(td, total_sessions=20)
        pos_recs = [r for r in recs if "Add submissions" in r["title"]]
        assert len(pos_recs) == 0


# =====================
# Intensity Recommendations
# =====================

class TestIntensityRecommendations:
    def _make_rpe_data(self, values, start_days_ago=None):
        now = datetime.utcnow()
        if start_days_ago is None:
            start_days_ago = len(values) - 1
        return [
            {"date": now - timedelta(days=start_days_ago - i), "rpe": v}
            for i, v in enumerate(values)
        ]

    def test_high_intensity_fires(self):
        rpe_data = self._make_rpe_data([8, 8, 9, 8, 8], start_days_ago=4)
        recs = recommend_intensity(rpe_data, total_sessions=10, active_injuries=[])
        assert any("High training intensity" in r["title"] for r in recs)

    def test_high_intensity_is_high_priority_when_injured(self):
        rpe_data = self._make_rpe_data([8, 8, 9, 8, 8], start_days_ago=4)
        recs = recommend_intensity(rpe_data, total_sessions=10, active_injuries=["knee"])
        high_recs = [r for r in recs if "High training intensity" in r["title"]]
        assert high_recs[0]["priority"] == "high"

    def test_high_intensity_is_medium_priority_when_healthy(self):
        rpe_data = self._make_rpe_data([8, 8, 9, 8, 8], start_days_ago=4)
        recs = recommend_intensity(rpe_data, total_sessions=10, active_injuries=[])
        high_recs = [r for r in recs if "High training intensity" in r["title"]]
        assert high_recs[0]["priority"] == "medium"

    def test_low_intensity_fires(self):
        rpe_data = self._make_rpe_data([3, 2, 3, 3, 2], start_days_ago=4)
        recs = recommend_intensity(rpe_data, total_sessions=5, active_injuries=[])
        assert any("Low intensity" in r["title"] for r in recs)

    def test_low_intensity_does_not_fire_with_few_sessions(self):
        rpe_data = self._make_rpe_data([3, 2], start_days_ago=1)
        recs = recommend_intensity(rpe_data, total_sessions=2, active_injuries=[])
        low_recs = [r for r in recs if "Low intensity" in r["title"]]
        assert len(low_recs) == 0

    def test_rising_trend_fires(self):
        rpe_data = self._make_rpe_data([5, 6, 7], start_days_ago=2)
        recs = recommend_intensity(rpe_data, total_sessions=10, active_injuries=[])
        assert any("Rising intensity" in r["title"] for r in recs)

    def test_rising_trend_does_not_fire_if_last_below_7(self):
        rpe_data = self._make_rpe_data([3, 4, 6], start_days_ago=2)
        recs = recommend_intensity(rpe_data, total_sessions=10, active_injuries=[])
        trend_recs = [r for r in recs if "Rising" in r["title"]]
        assert len(trend_recs) == 0

    def test_high_load_while_injured_fires(self):
        now = datetime.utcnow()
        rpe_data = [{"date": now - timedelta(days=i), "rpe": 7} for i in range(20)]
        recs = recommend_intensity(rpe_data, total_sessions=20, active_injuries=["shoulder"])
        assert any("injury" in r["title"].lower() for r in recs)

    def test_no_recs_with_empty_rpe(self):
        recs = recommend_intensity([], total_sessions=10, active_injuries=[])
        assert len(recs) == 0
