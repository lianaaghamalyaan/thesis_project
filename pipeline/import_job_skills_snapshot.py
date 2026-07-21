"""Apply an already-reviewed job_id -> skills snapshot to job_skills, without
calling any LLM. This is the production-side counterpart to
pipeline/promote_job_skills_v2.py, which did the actual extraction +
consolidation work locally (see its docstring for the full quality story:
old job_skills was capped at ~8 skills/posting; the v2 evidence-based
extraction fixed that; this file's job_id-keyed snapshot is that corrected,
audited, human-reviewed result).

Keyed by job_id (stable sha1(source_url)), not internal integer posting_id,
so it applies correctly regardless of what order rows were inserted in this
database. Every postings' job_skills rows are replaced with the snapshot's
list for that job_id; postings this database has that the snapshot doesn't
cover are left untouched.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.import_job_skills_snapshot [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SNAPSHOT_PATH = ROOT / "data/processed/unified/job_skills_v2_promoted_snapshot.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT_PATH)
    args = parser.parse_args()

    from server.db import SessionLocal
    from server.models import JobPosting, JobSkill

    snapshot: dict[str, list[str]] = json.loads(args.snapshot.read_text())
    print(f"Snapshot covers {len(snapshot)} postings, "
          f"{sum(len(v) for v in snapshot.values())} skill rows.")

    session = SessionLocal()
    try:
        job_id_to_posting_id = dict(
            session.query(JobPosting.job_id, JobPosting.id).all()
        )
        matched = {jid: pid for jid, pid in job_id_to_posting_id.items() if jid in snapshot}
        missing = set(snapshot) - set(job_id_to_posting_id)
        print(f"{len(matched)} of {len(snapshot)} snapshot postings found in this database "
              f"({len(missing)} not found — likely not yet imported here).")
        if missing:
            print(f"  Sample missing job_ids: {sorted(missing)[:5]}")

        if args.dry_run:
            print("Dry run — no writes.")
            return

        posting_ids = list(matched.values())
        deleted = session.query(JobSkill).filter(JobSkill.posting_id.in_(posting_ids)).delete(synchronize_session=False)
        print(f"Deleted {deleted} old job_skills rows for these {len(posting_ids)} postings.")

        n_inserted = 0
        for job_id, posting_id in matched.items():
            for skill in set(snapshot[job_id]):
                session.add(JobSkill(
                    posting_id=posting_id,
                    skill_name=skill,
                    extraction_method="LLM",
                    prompt_version="v2_promoted_job_skills_v2_20260715",
                ))
                n_inserted += 1
        session.commit()

        from sqlalchemy import text
        total_distinct = session.execute(text("SELECT COUNT(DISTINCT skill_name) FROM job_skills")).scalar_one()
        print(f"\nInserted {n_inserted} job_skills rows. Distinct skill_name count now: {total_distinct}.")
        print("Next: pipeline/build_skill_embeddings.py, then pipeline/compute_alignment.py (unscoped), then review.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
