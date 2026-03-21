from datetime import datetime, timezone, timedelta

now = datetime.now(timezone.utc)
print(f"Current system time: {now}")
print(f"30 days ago: {now - timedelta(days=30)}")

# Your entries
entries = [
    "2026-01-26 02:00:00",
    "2026-02-15 02:00:00", 
    "2026-02-13 02:00:00"
]

print("\nYour entries:")
for e in entries:
    entry_date = datetime.fromisoformat(e).replace(tzinfo=timezone.utc)
    print(f"  {e} - {'INCLUDED' if entry_date >= (now - timedelta(days=30)) else 'EXCLUDED'}")
