from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.database import get_db
from app.models import Entry, Response, Question, User, InjuryLog
from app.dependencies import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_entries_with_responses(db: Session, user_id: int, days: int = 90):
    """Fetch entries and their responses for a user within the last N days."""
    since = datetime.now() - timedelta(days=days)
    entries = (
        db.query(Entry)
        .filter(Entry.user_id == user_id, Entry.date >= since)
        .order_by(Entry.date.desc())
        .all()
    )
    entry_ids = [e.id for e in entries]
    responses = (
        db.query(Response)
        .options(joinedload(Response.question))
        .filter(Response.entry_id.in_(entry_ids))
        .all()
    ) if entry_ids else []
    return entries, responses


def get_active_injuries(db: Session, user_id: int) -> List[str]:
    """Return list of injured area names that are currently active."""
    injuries = db.query(InjuryLog).filter(
        InjuryLog.user_id == user_id,
        InjuryLog.end_date.is_(None)
    ).all()
    return [i.injured_area.lower() for i in injuries]


def extract_rpe_values(entries: List, responses: List) -> List[Dict]:
    """Return list of {date, rpe} dicts sorted oldest to newest."""
    result = []
    for entry in entries:
        rpe = next(
            (int(r.answer) for r in responses
             if r.entry_id == entry.id
             and r.question
             and "Rate of Perceived Exertion" in r.question.question_text
             and r.answer.isdigit()),
            None
        )
        if rpe is not None:
            result.append({"date": entry.date, "rpe": rpe})
    return sorted(result, key=lambda x: x["date"])


def extract_technique_data(responses: List) -> Dict[str, Any]:
    """
    Parse Class Technique responses into position and skill type frequency maps.
    Returns:
        position_counts: {position: count}
        skill_counts: {skill_type: count}
        position_last_seen: {position: datetime}
        position_skills: {position: {skill_type: count}}
    """
    position_counts: Dict[str, int] = {}
    skill_counts: Dict[str, int] = {}
    position_last_seen: Dict[str, datetime] = {}
    position_skills: Dict[str, Dict[str, int]] = {}

    technique_responses = [
        r for r in responses
        if r.question and "Class Technique" in r.question.question_text
        and " - " in r.answer
    ]

    for r in technique_responses:
        parts = r.answer.split(" - ")
        if len(parts) < 2:
            continue
        position = parts[0].strip()
        skill = parts[1].strip()

        position_counts[position] = position_counts.get(position, 0) + 1
        skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Track last seen date per position
        entry_date = r.entry.date if hasattr(r, 'entry') and r.entry else datetime.min
        if position not in position_last_seen or entry_date > position_last_seen[position]:
            position_last_seen[position] = entry_date

        # Track skills per position
        if position not in position_skills:
            position_skills[position] = {}
        position_skills[position][skill] = position_skills[position].get(skill, 0) + 1

    return {
        "position_counts": position_counts,
        "skill_counts": skill_counts,
        "position_last_seen": position_last_seen,
        "position_skills": position_skills,
    }


def build_recommendation(type_: str, priority: str, title: str, message: str, action: str, data: Dict = None):
    return {
        "type": type_,
        "priority": priority,
        "title": title,
        "message": message,
        "action": action,
        "data": data or {}
    }


def recommend_positions(technique_data: Dict, active_injuries: List[str]) -> List[Dict]:
    recs = []
    position_counts = technique_data["position_counts"]
    position_last_seen = technique_data["position_last_seen"]
    position_skills = technique_data["position_skills"]
    now = datetime.now()

    # Rule 1 - Stale position (medium)
    for position, last_seen in position_last_seen.items():
        days_ago = (now - last_seen).days
        if days_ago >= 30:
            recs.append(build_recommendation(
                type_="position",
                priority="medium",
                title=f"Revisit {position}",
                message=f"You haven't trained {position} in {days_ago} days.",
                action=f"Log a session focused on {position}.",
                data={"position": position, "days_since_trained": days_ago}
            ))

    # Rule 2 - Limited skill diversity (low)
    for position, skills in position_skills.items():
        if position_counts.get(position, 0) >= 3 and len(skills) == 1:
            only_skill = list(skills.keys())[0]
            recs.append(build_recommendation(
                type_="position",
                priority="low",
                title=f"Expand your {position} game",
                message=f"You've trained {position} {position_counts[position]} times, but only focused on {only_skill}.",
                action="Incorporate additional skill types such as sweeps, escapes, or transitions.",
                data={"position": position, "current_skill": only_skill, "count": position_counts[position]}
            ))

    # Rule 3 - No guard passing at all (high)
    guard_positions = [p for p in position_counts if "Guard" in p and "Passing" not in p]
    passing_positions = [p for p in position_counts if "Pass" in p or p in ["Guard Passing"]]
    guard_total = sum(position_counts[p] for p in guard_positions)
    passing_total = sum(position_counts[p] for p in passing_positions)

    if guard_total >= 5 and passing_total == 0:
        recs.append(build_recommendation(
            type_="position",
            priority="high",
            title="Prioritise guard passing",
            message=f"You've logged {guard_total} guard sessions but no guard passing work in the past 90 days.",
            action="Add a guard passing-focused session.",
            data={"guard_sessions": guard_total, "passing_sessions": passing_total}
        ))
    elif guard_total > 0 and passing_total > 0 and guard_total / max(passing_total, 1) >= 4:
        # Rule 4 - Guard/passing imbalance (medium)
        recs.append(build_recommendation(
            type_="position",
            priority="medium",
            title="Address guard passing imbalance",
            message=f"You've trained guard {guard_total} times but only passed {passing_total} times.",
            action="Log a session focused on guard passing to improve balance.",
            data={"guard_sessions": guard_total, "passing_sessions": passing_total}
        ))

    return recs


def recommend_submissions(technique_data: Dict, total_sessions: int) -> List[Dict]:
    recs = []
    skill_counts = technique_data["skill_counts"]
    position_skills = technique_data["position_skills"]
    position_counts = technique_data["position_counts"]

    attack_count = skill_counts.get("Attacks/Submissions", 0)

    # Rule 1 - Low submission frequency (high)
    if total_sessions >= 5 and attack_count / total_sessions < 0.2:
        recs.append(build_recommendation(
            type_="submission",
            priority="high",
            title="Increase submission focus",
            message=f"Submissions were included in {attack_count} of your last {total_sessions} sessions ({int(attack_count/total_sessions*100)}%).",
            action="Prioritise attacks and submissions in your next session.",
            data={"submission_sessions": attack_count, "total_sessions": total_sessions}
        ))

    # Rule 2 - No submissions from position (medium)
    for position, skills in position_skills.items():
        count = sum(skills.values())
        has_attacks = "Attacks/Submissions" in skills
        if count >= 4 and not has_attacks:
            recs.append(build_recommendation(
                type_="submission",
                priority="medium",
                title=f"Add submissions from {position}",
                message=f"You've trained {position} {count} times without working on submissions.",
                action="Explore and drill submission options from this position.",
                data={"position": position, "sessions": count}
            ))

    return recs


def recommend_intensity(rpe_data: List[Dict], total_sessions: int, active_injuries: List[str]) -> List[Dict]:
    recs = []

    if not rpe_data:
        return recs

    week_ago = datetime.now() - timedelta(days=7)
    recent_rpe = [r["rpe"] for r in rpe_data if r["date"] >= week_ago]
    avg_recent = sum(recent_rpe) / len(recent_rpe) if recent_rpe else None

    month_ago = datetime.now() - timedelta(days=30)
    month_rpe = [r["rpe"] for r in rpe_data if r["date"] >= month_ago]
    avg_month = sum(month_rpe) / len(month_rpe) if month_rpe else None

    if avg_recent is not None:
        # Rule 1 - High training intensity (medium, or high if injured)
        if avg_recent > 7.5:
            priority = "high" if active_injuries else "medium"
            msg = f"Your average RPE over the past 7 days is {avg_recent:.1f}/9."
            if active_injuries:
                msg += f" With an active injury ({', '.join(active_injuries)}), this increases your recovery risk."
            recs.append(build_recommendation(
                type_="intensity",
                priority=priority,
                title="High training intensity detected",
                message=msg,
                action="Schedule a lower-intensity technical or drilling session.",
                data={"avg_rpe_7d": round(avg_recent, 1), "active_injuries": active_injuries}
            ))
        # Rule 2 - Low training intensity (low)
        elif avg_recent < 4.0 and total_sessions >= 3:
            recs.append(build_recommendation(
                type_="intensity",
                priority="low",
                title="Low intensity week",
                message=f"Your average RPE over the past 7 days is {avg_recent:.1f}/9. You may be ready to increase intensity.",
                action="Consider adding a higher-intensity sparring session.",
                data={"avg_rpe_7d": round(avg_recent, 1)}
            ))

    # Rule 3 - Increasing intensity trend (medium)
    if len(rpe_data) >= 3:
        last_three = [r["rpe"] for r in rpe_data[-3:]]
        if last_three[0] < last_three[1] < last_three[2] and last_three[2] >= 7:
            recs.append(build_recommendation(
                type_="intensity",
                priority="medium",
                title="Rising intensity trend",
                message=f"Your last three sessions have increased in intensity ({last_three[0]} → {last_three[1]} → {last_three[2]}).",
                action="Plan a recovery or technical session to avoid overtraining.",
                data={"rpe_trend": last_three}
            ))

    # Rule 4 - High load while injured (high)
    if active_injuries and avg_month and avg_month > 6.5:
        recs.append(build_recommendation(
            type_="intensity",
            priority="high",
            title="High intensity during injury",
            message=f"You have active injuries ({', '.join(active_injuries)}) and a monthly average RPE of {avg_month:.1f}/9.",
            action="Reduce training intensity and protect the affected areas.",
            data={"avg_rpe_30d": round(avg_month, 1), "active_injuries": active_injuries}
        ))

    return recs


@router.get("/")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    entries, responses = get_entries_with_responses(db, current_user.id, days=90)
    active_injuries = get_active_injuries(db, current_user.id)
    technique_data = extract_technique_data(responses)
    rpe_data = extract_rpe_values(entries, responses)

    total_sessions = len(entries)

    all_recs = []
    all_recs += recommend_positions(technique_data, active_injuries)
    all_recs += recommend_submissions(technique_data, total_sessions)
    all_recs += recommend_intensity(rpe_data, total_sessions, active_injuries)

    # Sort by priority: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_recs.sort(key=lambda r: priority_order.get(r["priority"], 3))

    # Return only the top 1 recommendation per type
    seen_types = set()
    filtered_recs = []
    for rec in all_recs:
        if rec["type"] not in seen_types:
            seen_types.add(rec["type"])
            filtered_recs.append(rec)

    return {
        "total": len(filtered_recs),
        "recommendations": filtered_recs,
        "meta": {
            "sessions_analysed": total_sessions,
            "active_injuries": active_injuries,
            "positions_tracked": len(technique_data["position_counts"]),
            "rpe_data_points": len(rpe_data),
            "low_data": total_sessions < 5
        }
    }
