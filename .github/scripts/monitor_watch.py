"""A1 (spec seguranca-doacoes, section 3): whether the monitor's chain check ran recently. It runs every 15 minutes; a newest run older
than three of those intervals means the monitor stopped (or GitHub turned its schedule off), and the hourly job here fails, which
GitHub e-mails as the alarm.

Run: python3 .github/scripts/monitor_watch.py <created_at of the newest run, or nothing>
"""
import datetime
import sys

LIMIT = datetime.timedelta(minutes=45)


def stale(created_at, now):
    if not created_at:
        return True
    when = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    return now - when > LIMIT


if __name__ == "__main__":
    last = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] not in ("", "null") else None
    if stale(last, datetime.datetime.now(datetime.timezone.utc)):
        print(f"::error::the monitor's chain check has not run in {int(LIMIT.total_seconds() // 60)} minutes (newest run: {last or 'none'})")
        sys.exit(1)
    print(f"the monitor ran at {last}")
