#!/bin/sh
# Waits for the database, seeds it on first boot only (if the `universities`
# table doesn't exist yet — safe to leave this running on every deploy), then
# starts the dashboard.
set -e

echo "Waiting for database at ${DATABASE_URL:-<unset>} ..."
python - <<'PYEOF'
import os, sys, time
sys.path.insert(0, ".")
from sqlalchemy import create_engine, text
url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL is not set — refusing to start.", file=sys.stderr)
    sys.exit(1)
engine = create_engine(url)
for attempt in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is reachable.")
        break
    except Exception as e:
        print(f"  attempt {attempt+1}/30: {e}")
        time.sleep(2)
else:
    print("Database never became reachable.", file=sys.stderr)
    sys.exit(1)
PYEOF

echo "Checking whether the schema needs seeding ..."
python - <<'PYEOF'
import sys
sys.path.insert(0, ".")
from sqlalchemy import inspect
from server.db import engine

inspector = inspect(engine)
if "universities" not in inspector.get_table_names():
    print("Schema not found — running initial seed (this loads all processed data; takes ~1-2 min).")
    import server.seed as seed
    seed.main()
else:
    print("Schema already present — skipping seed. (Re-run `python -m server.seed` manually to reload data.)")
PYEOF

echo "Starting Streamlit ..."
exec streamlit run dashboard/app.py \
    --server.address 0.0.0.0 \
    --server.port "${PORT:-8501}" \
    --server.headless true
