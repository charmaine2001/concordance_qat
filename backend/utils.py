# utils.py
from datetime import datetime, timedelta, timezone

def compute_range(filter_name: str):
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    if filter_name == "today":
        return today_start, now
    if filter_name == "yesterday":
        start = today_start - timedelta(days=1)
        end = today_start
        return start, end
    if filter_name == "last_week":
        start = today_start - timedelta(days=7)
        return start, now
    if filter_name == "last_month":
        start = today_start - timedelta(days=30)
        return start, now
    # default: last 24 hours
    return now - timedelta(days=1), now
