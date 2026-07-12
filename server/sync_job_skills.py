"""Incremental sync: push any job_id -> skills entries from
data/processed/unified/job_skills_by_id.json that aren't in the job_skills
table yet. Unlike server/seed.py, this does NOT drop/recreate tables — safe
to run after passwords or other live data have been set.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.sync_job_skills
"""
from __future__ import annotations

import json
from pathlib import Path

from .db import SessionLocal
from .models import JobPosting
from .seed import bulk_insert

ROOT = Path(__file__).resolve().parents[1]
SKILLS_JSON = ROOT / "data/processed/unified/job_skills_by_id.json"


def main() -> None:
    with open(SKILLS_JSON) as f:
        job_skills_raw = json.load(f)

    session = SessionLocal()
    try:
        postings = session.query(JobPosting.id, JobPosting.job_id).all()
        posting_pk_by_job_id = {job_id: pk for pk, job_id in postings}

        existing_posting_ids_with_skills = {
            row[0] for row in session.execute(
                __import__("sqlalchemy").text("SELECT DISTINCT posting_id FROM job_skills")
            )
        }

        new_rows = []
        n_new_postings = 0
        for job_id, skills in job_skills_raw.items():
            pk = posting_pk_by_job_id.get(job_id)
            if pk is None or pk in existing_posting_ids_with_skills:
                continue
            n_new_postings += 1
            for skill in skills:
                new_rows.append((pk, skill, "LLM", "job_skills_v1_2026-07-10"))

        bulk_insert(
            session, "job_skills",
            ["posting_id", "skill_name", "extraction_method", "prompt_version"],
            new_rows,
        )
        session.commit()
        print(f"Synced {n_new_postings} newly-extracted postings, {len(new_rows)} skill rows.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
