"""
Seed dummy training data via the API — works against any environment.
Usage:
    python seed_production.py --user demo --password demo123                # local
    python seed_production.py --prod --user demo --password demo123        # production
    python seed_production.py --prod --user demo --password demo123 --days 90
"""
import argparse
import random
import requests
from datetime import datetime, timedelta

random.seed(99)

LOCAL_URL = "http://localhost:8000"
PROD_URL = "https://bjjjournal-production.up.railway.app"

SESSION_TYPES = ["Gi", "No Gi"]
TRAINING_TYPES = [
    "Regular Class", "Open Mat", "Competition Training", "Drilling Session",
    "Private Lesson", "Light Training", "Competition"
]
POSITIONS = [
    "Closed Guard", "Open Guard", "Half Guard", "Butterfly Guard",
    "De La Riva Guard", "X-Guard", "Spider Guard", "Side Control",
    "Mount", "Back Control", "North-South", "Knee on Belly",
    "Stand up", "Wrestling", "Guard Pulling", "50/50 Guard",
    "Knee Shield Half Guard", "Deep Half Guard", "Ashi Garami",
    "Turtle Guard", "Kesa Gatame", "High Mount",
]
SKILL_TYPES = [
    "Attacks/Submissions", "Sweeps", "Escapes", "Defense",
    "Setups", "Transitions", "Guard Passing"
]
SUBMISSIONS = [
    "Armbar", "Kimura", "Americana", "Triangle Choke", "Rear Naked Choke",
    "Guillotine Choke", "Omoplata", "Heel Hook", "Straight Ankle Lock",
    "Bow and Arrow Choke", "D'Arce Choke", "Ezekiel Choke", "Wrist Lock",
    "Kneebar", "Toe Hold", "Loop Choke", "Baseball Bat Choke",
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
    "Focused on passing today, felt good.",
    "Leg lock entries getting sharper.",
]
SUMMARIES = [
    "Solid session", "Tough but good", "Technical day",
    "High intensity", "Recovery session", "Great drilling",
    "Competitive sparring", "Focused on basics", "Submission hunting",
    "Guard work", "Top game focus", "Takedown practice",
]


def login(base_url, username, password):
    r = requests.post(f"{base_url}/auth/login", json={"username": username, "password": password})
    if r.status_code != 200:
        print(f"Login failed ({r.status_code}): {r.text}")
        return None
    return r.json()["access_token"]


def get_questions(base_url, token):
    r = requests.get(f"{base_url}/questions/", headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 200:
        return r.json()
    # Try without auth (some setups don't require it for questions)
    r = requests.get(f"{base_url}/questions/")
    return r.json() if r.status_code == 200 else []


def pick_technique():
    pos = random.choice(POSITIONS)
    skill = random.choice(SKILL_TYPES)
    if skill == "Attacks/Submissions":
        return f"{pos} - {random.choice(SUBMISSIONS)}"
    return f"{pos} - {skill}"


def generate_sessions(days):
    sessions = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)
    current = start
    while current <= today:
        week_sessions = random.randint(5, 6)
        week_days = random.sample(range(7), min(week_sessions, 7))
        for day_offset in sorted(week_days):
            session_date = current + timedelta(days=day_offset)
            if session_date <= today:
                hour = random.choice([7, 8, 9, 18, 19, 20])
                session_date = session_date.replace(hour=hour, minute=random.randint(0, 59))
                sessions.append(session_date)
        current += timedelta(days=7)
    return sessions


def build_responses(questions, training_type):
    if training_type == "Drilling Session":
        rpe = random.randint(3, 5)
        rounds = random.randint(6, 9)
    elif training_type in ("Competition Training", "Open Mat", "Competition"):
        rpe = random.randint(7, 9)
        rounds = random.randint(6, 9)
    elif training_type == "Light Training":
        rpe = random.randint(1, 3)
        rounds = random.randint(6, 9)
    else:
        rpe = random.randint(4, 7)
        rounds = random.randint(6, 9)

    session_type = random.choice(SESSION_TYPES)
    technique = pick_technique()
    notes = random.choice(NOTES)
    summary = random.choice(SUMMARIES)

    q_map = {q["question_text"]: q["id"] for q in questions}
    responses = []

    if "Session Type" in q_map:
        responses.append({"question_id": q_map["Session Type"], "answer": session_type})
    if "Rate of Perceived Exertion (RPE)" in q_map:
        responses.append({"question_id": q_map["Rate of Perceived Exertion (RPE)"], "answer": str(rpe)})
    else:
        # Partial match for RPE question
        for text, qid in q_map.items():
            if "perceived exertion" in text.lower() or "rpe" in text.lower():
                responses.append({"question_id": qid, "answer": str(rpe)})
                break
    if "Training" in q_map:
        responses.append({"question_id": q_map["Training"], "answer": training_type})
    if "Class Technique" in q_map:
        responses.append({"question_id": q_map["Class Technique"], "answer": technique})
    if "Rounds Rolled" in q_map:
        responses.append({"question_id": q_map["Rounds Rolled"], "answer": str(rounds)})
    if "Journal Notes" in q_map:
        responses.append({"question_id": q_map["Journal Notes"], "answer": notes})
    if "Summarise this session with a few words" in q_map:
        responses.append({"question_id": q_map["Summarise this session with a few words"], "answer": summary})

    return responses


def seed(base_url, username, password, days):
    print(f"Target: {base_url}")
    print(f"User: {username}")
    print(f"Days: {days}")

    token = login(base_url, username, password)
    if not token:
        return

    questions = get_questions(base_url, token)
    if not questions:
        print("No questions found — check the API.")
        return

    print(f"Found {len(questions)} questions: {[q['question_text'] for q in questions]}")

    sessions = generate_sessions(days)
    print(f"Generating {len(sessions)} sessions over {days} days...", flush=True)

    success = 0
    failed = 0
    for i, date in enumerate(sessions):
        training_type = random.choice(TRAINING_TYPES)
        responses = build_responses(questions, training_type)

        entry_data = {
            "date": date.isoformat(),
            "session_type": "training",
            "responses": responses
        }

        r = requests.post(
            f"{base_url}/entries/",
            json=entry_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        if r.status_code in (200, 201):
            success += 1
            if success <= 3:
                print(f"  Entry {i+1} created OK", flush=True)
        else:
            failed += 1
            if failed <= 3:
                print(f"  Failed entry {i+1}: {r.status_code} - {r.text[:200]}")

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(sessions)}", flush=True)

    print(f"\nDone. {success} created, {failed} failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed dummy training data via API")
    parser.add_argument("--prod", action="store_true", help="Target production")
    parser.add_argument("--user", required=True, help="Username to seed data for")
    parser.add_argument("--password", required=True, help="Password for the user")
    parser.add_argument("--days", type=int, default=60, help="Days of data to generate (default: 60)")
    args = parser.parse_args()

    base = PROD_URL if args.prod else LOCAL_URL
    seed(base, args.user, args.password, args.days)
