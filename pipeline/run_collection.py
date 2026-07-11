"""Orchestrator: run all scrapers, write per-run snapshot metadata.

Usage:
    python pipeline/run_collection.py

Each scraper appends new rows to its raw CSV in data/raw/jobs/.
A snapshot record is written to data/runs/YYYY-MM-DD/metadata.json.
The frozen March 2026 data is never touched.
"""
from __future__ import annotations

import json
import sys
import traceback
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.scrapers import (
    betconstruct,
    dataart,
    disqo,
    epam,
    griddynamics,
    jobam,
    krisp,
    myjob,
    nvidia,
    picsart,
    servicetitan,
    softconstruct,
    staffam,
    superannotate,
    synopsys,
    teamviewer,
    tenweb,
)

SCRAPERS = [
    ("job.am", jobam),
    ("staff.am", staffam),
    ("myjob.am", myjob),
    ("picsart", picsart),
    ("disqo", disqo),
    ("superannotate", superannotate),
    ("10web", tenweb),
    ("epam", epam),
    ("krisp", krisp),
    ("softconstruct", softconstruct),
    ("synopsys", synopsys),
    ("betconstruct", betconstruct),
    ("teamviewer", teamviewer),
    ("dataart", dataart),
    ("servicetitan", servicetitan),
    ("griddynamics", griddynamics),
    ("nvidia", nvidia),
]


def main() -> None:
    today = date.today().isoformat()
    print(f"=== Job Collection Run: {today} ===\n")

    results: dict[str, int] = {}
    errors: dict[str, str] = {}

    for name, module in SCRAPERS:
        print(f"--- {name} ---")
        try:
            records = module.scrape()
            results[name] = len(records)
        except Exception:
            tb = traceback.format_exc()
            print(f"  ERROR in {name}:\n{tb}")
            errors[name] = tb.strip().splitlines()[-1]
            results[name] = 0

    total_new = sum(results.values())
    print(f"\n=== Summary ===")
    print(f"Total new jobs: {total_new}")
    for name, count in results.items():
        status = f"{count} new" if name not in errors else f"ERROR: {errors[name]}"
        print(f"  {name:<20} {status}")

    snapshot_dir = ROOT / "data" / "runs" / today
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "run_date": today,
        "total_new_jobs": total_new,
        "new_jobs_per_source": results,
        "errors": errors,
        "note": "Phase A collection run — raw data only, alignment scores not updated",
    }
    with open(snapshot_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nSnapshot metadata written to data/runs/{today}/metadata.json")


if __name__ == "__main__":
    main()
