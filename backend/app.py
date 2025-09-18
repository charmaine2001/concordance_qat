import os
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()  # optional - load config from .env

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "first task done...now moving on to the hard parts..."


SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PKEY = os.getenv("SSH_KEY_PATH")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

LOCAL_BIND_PORT = int(os.getenv("LOCAL_BIND_PORT", "6543"))
REMOTE_DB_HOST = os.getenv("REMOTE_DB_HOST", "127.0.0.1")
REMOTE_DB_PORT = int(os.getenv("REMOTE_DB_PORT", "5432"))

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")





@contextmanager
def open_ssh_tunnel():
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_pkey=SSH_PKEY,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
        local_bind_address=("127.0.0.1", LOCAL_BIND_PORT),
    )
    tunnel.start()
    try:
        print(f"SSH tunnel open: localhost:{tunnel.local_bind_port} -> {REMOTE_DB_HOST}:{REMOTE_DB_PORT}")
        yield tunnel.local_bind_port
    finally:
        tunnel.stop()
        print("SSH tunnel closed.")


def make_engine(local_port):
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@127.0.0.1:{local_port}/master"
    engine = create_engine(url, pool_size=5, max_overflow=10)
    return engine


def compute_range(filter_name: str):
    # returns start_ts, end_ts as timezone-aware UTC datetimes
    now = datetime.now(timezone.utc)
    # normalize to start of day UTC
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    if filter_name == "today":
        start = today_start
        end = start + timedelta(days=1)
    elif filter_name == "yesterday":
        start = today_start - timedelta(days=1)
        end = today_start
    elif filter_name == "last_week":
        # last 7 days (including today)
        start = today_start - timedelta(days=6)
        end = today_start + timedelta(days=1)
    elif filter_name == "last_month":
        # last 30 days
        start = today_start - timedelta(days=29)
        end = today_start + timedelta(days=1)
    else:
        # default -> last 7 days
        start = today_start - timedelta(days=6)
        end = today_start + timedelta(days=1)
    return start, end

SQL_COUNT_BY_DAY = text("""
SELECT 
  facility_id,
  date_trunc('day', created_at AT TIME ZONE 'UTC')::date AS day,
  count(*)::int AS cnt
FROM report.attendance_dpl
WHERE created_at >= :start_ts
  AND created_at < :end_ts
GROUP BY facility_id, day
ORDER BY facility_id, day;
""")

@app.route("/api/attendance_counts")
def attendance_counts():
    """
    Query params:
      - filter: today | yesterday | last_week | last_month
    Returns JSON: [{ "facility_id": "...", "date": "YYYY-MM-DD", "count": N }, ...]
    """
    filter_name = request.args.get("filter", "last_week")
    start_ts, end_ts = compute_range(filter_name)

    # Open SSH tunnel and perform query
    with open_ssh_tunnel() as local_port:
        engine = make_engine(local_port)
        with engine.connect() as conn:
            rows = conn.execute(
                SQL_COUNT_BY_DAY, {"start_ts": start_ts, "end_ts": end_ts}
            ).mappings().all()   # 👈 rows are dict-like

        out = [
            {"facility_id": r["facility_id"], "date": r["day"].isoformat(), "count": r["cnt"]}
            for r in rows
        ]
    return jsonify(out)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
