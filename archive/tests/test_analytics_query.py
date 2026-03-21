from app.database import SessionLocal
from app.models import User, Entry
from datetime import datetime, timedelta, timezone

db = SessionLocal()
user = db.query(User).filter(User.username == 'test').first()

now = datetime.now(timezone.utc)
start_date = now - timedelta(days=30)

print(f"Now: {now}")
print(f"Start date: {start_date}")
print(f"Start date (no tz): {start_date.replace(tzinfo=None)}")

# Test with timezone
entries_with_tz = db.query(Entry).filter(
    Entry.user_id == user.id,
    Entry.date >= start_date
).all()
print(f"\nWith timezone: {len(entries_with_tz)} entries")

# Test without timezone
entries_no_tz = db.query(Entry).filter(
    Entry.user_id == user.id,
    Entry.date >= start_date.replace(tzinfo=None)
).all()
print(f"Without timezone: {len(entries_no_tz)} entries")

# Test all entries
all_entries = db.query(Entry).filter(Entry.user_id == user.id).all()
print(f"All entries: {len(all_entries)} entries")
for e in all_entries:
    print(f"  Entry {e.id}: date={e.date}, type={type(e.date)}")

db.close()
