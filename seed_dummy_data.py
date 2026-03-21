"""
Seed 60 days of dummy training data for user 'test'.
Avg 3-6 sessions/week with varying intensity, positions, and techniques.
"""
import random
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import User, Entry, Response

random.seed(42)

SESSION_TYPES = ["Gi", "No Gi", "Both"]
TRAINING_TYPES = ["Class", "Open Mat", "Competition", "Drilling", "Private"]
POSITIONS = [
    "Closed Guard", "Open Guard", "Half Guard", "Butterfly Guard",
    "De La Riva Guard", "X-Guard", "Spider Guard", "Side Control",
    "Mount", "Back Control", "North-South", "Knee on Belly",
    "Stand up", "Wrestling", "Guard Pulling", "50/50 Guard",
]
SKILL_TYPES = [
    "Attacks/Submissions", "Sweeps", "Escapes", "Defense",
    "Setups", "Transitions", "Guard Passing"
]
NOTES = [
    "Good session, felt sharp today.",
    "Struggled with timing on takedowns.",
    "Worked on maintaining back control.",
    "Drilled a lot, less sparring.",
    "Felt tired but pushed through.",
    "Great rolls, caught a few submissions.",
    "Focused on defence today.",
    "Technique felt smooth.",
    "Hard session, high intensity.",
    "Light drilling, recovery day.",
    "Worked on guard retention.",
    "Sparred with higher belts, learned a lot.",
]
SUMMARIES = [
    "Solid session", "Tough but good", "Technical day",
    "High intensity", "Recovery session", "Great drilling",
    "Competitive sparring", "Focused on basics", "Submission hunting",
    "Guard work", "Top game focus", "Takedown practice",
]


def pick_technique():
    position = random.choice(POSITIONS)
    skill = random.choice(SKILL_TYPES)
    return f"{position} - {skill}"


def generate_sessions(days=60):
    """Generate session dates spread over the last 60 days, 3-6 per week."""
    sessions = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

    current = start
    while current <= today:
        # Start of week - decide how many sessions this week (3-6)
        week_sessions = random.randint(3, 6)
        week_days = random.sample(range(7), min(week_sessions, 7))
        for day_offset in sorted(week_days):
            session_date = current + timedelta(days=day_offset)
            if session_date <= today:
                # Vary time of day (morning/evening)
                hour = random.choice([7, 8, 9, 18, 19, 20])
                session_date = session_date.replace(hour=hour, minute=random.randint(0, 59))
                sessions.append(session_date)
        current += timedelta(days=7)

    return sessions


def build_responses(entry_id, session_type, rpe, training_type, technique, rounds, notes, summary):
    return [
        Response(entry_id=entry_id, question_id=1, answer=session_type),
        Response(entry_id=entry_id, question_id=2, answer=str(rpe)),
        Response(entry_id=entry_id, question_id=3, answer=training_type),
        Response(entry_id=entry_id, question_id=4, answer=technique),
        Response(entry_id=entry_id, question_id=5, answer=str(rounds)),
        Response(entry_id=entry_id, question_id=6, answer=notes),
        Response(entry_id=entry_id, question_id=7, answer=summary),
    ]


def seed():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "test").first()
        if not user:
            print("User 'test' not found. Create the user first.")
            return

        sessions = generate_sessions(days=60)
        print(f"Generating {len(sessions)} sessions over 60 days...")

        for date in sessions:
            # Vary intensity: weekday class = moderate, open mat = high, drilling = low
            training_type = random.choice(TRAINING_TYPES)
            if training_type == "Drilling":
                rpe = random.randint(3, 5)
                rounds = random.randint(0, 3)
            elif training_type in ("Competition", "Open Mat"):
                rpe = random.randint(7, 9)
                rounds = random.randint(6, 12)
            else:
                rpe = random.randint(5, 8)
                rounds = random.randint(3, 8)

            session_type = random.choice(SESSION_TYPES)
            technique = pick_technique()
            notes = random.choice(NOTES)
            summary = random.choice(SUMMARIES)

            entry = Entry(
                user_id=user.id,
                date=date,
                session_type=session_type,
                injured_during_session=False,
            )
            db.add(entry)
            db.flush()  # get entry.id

            for r in build_responses(entry.id, session_type, rpe, training_type, technique, rounds, notes, summary):
                db.add(r)

        db.commit()
        print(f"Done. {len(sessions)} sessions added for user '{user.username}'.")

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
