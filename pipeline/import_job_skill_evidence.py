"""Populate the job-skill *evidence* audit tables from a job_id-keyed snapshot.

This closes the gap that left production's Evidence Explorer job-side empty
after the July 2026 refresh: import_job_skills_snapshot.py replaces the
score-bearing job_skills rows (skill names only), but the evidence quotes
live in the separate job_skill_extraction_* tables, which the names snapshot
doesn't touch. This importer fills them from job_skill_evidence_snapshot.json
(produced by export_job_skill_evidence.py), keyed by job_id so it is safe on
any database regardless of local autoincrement ids.

Idempotent: if a completed run with the same run_key already exists, it is
left as-is unless --replace is passed. Belongs in the refresh sequence right
after the job_skills snapshot import — see run_remaining_refresh_steps.py.

    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.import_job_skill_evidence [--dry-run] [--replace]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SNAPSHOT_PATH = ROOT / "data/processed/unified/job_skill_evidence_snapshot.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace", action="store_true", help="delete an existing run with the same run_key first")
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT_PATH)
    args = parser.parse_args()

    from server.db import SessionLocal
    from server.models import (
        JobPosting,
        JobSkillExtractionPosting,
        JobSkillExtractionRun,
        JobSkillExtractionSkill,
    )

    payload = json.loads(args.snapshot.read_text())
    run_meta = payload["run"]
    by_job: dict[str, list[dict]] = payload["by_job_id"]
    run_key = run_meta["run_key"]
    total_skills = sum(len(v) for v in by_job.values())
    print(f"Snapshot: run {run_key}, {len(by_job)} postings, {total_skills} skill rows.")

    session = SessionLocal()
    try:
        existing = session.query(JobSkillExtractionRun).filter(JobSkillExtractionRun.run_key == run_key).first()
        if existing and not args.replace:
            print(f"Run {run_key} already present (id={existing.id}) — nothing to do. Pass --replace to rebuild.")
            return

        job_id_to_pid = dict(session.query(JobPosting.job_id, JobPosting.id).all())
        matched = {j: job_id_to_pid[j] for j in by_job if j in job_id_to_pid}
        missing = set(by_job) - set(job_id_to_pid)
        print(f"{len(matched)} of {len(by_job)} snapshot postings found in this database ({len(missing)} missing).")

        if args.dry_run:
            print("Dry run — no writes.")
            return

        if existing and args.replace:
            # ORM cascade isn't configured across these tables; delete children first.
            ep_ids = [r[0] for r in session.query(JobSkillExtractionPosting.id).filter(JobSkillExtractionPosting.run_id == existing.id)]
            if ep_ids:
                session.query(JobSkillExtractionSkill).filter(
                    JobSkillExtractionSkill.extraction_posting_id.in_(ep_ids)
                ).delete(synchronize_session=False)
            session.query(JobSkillExtractionPosting).filter(
                JobSkillExtractionPosting.run_id == existing.id
            ).delete(synchronize_session=False)
            session.delete(existing)
            session.flush()

        run = JobSkillExtractionRun(
            run_key=run_key,
            model_name=run_meta.get("model_name", "unknown"),
            prompt_version=run_meta.get("prompt_version", "unknown"),
            status="completed",
            expected_postings=run_meta.get("expected_postings", len(by_job)),
            completed_at=datetime.utcnow(),
            notes="Imported from job_skill_evidence_snapshot.json (job_id-keyed).",
        )
        session.add(run)
        session.flush()

        n_post = n_skill = 0
        for job_id, pid in matched.items():
            ep = JobSkillExtractionPosting(
                run_id=run.id,
                posting_id=pid,
                input_hash="",  # not carried in the snapshot; audit-only field
            )
            session.add(ep)
            session.flush()
            n_post += 1
            seen: set[str] = set()
            for s in by_job[job_id]:
                norm = s["normalized_skill_name"]
                if norm in seen:  # table has a (posting, normalized_skill) unique constraint
                    continue
                seen.add(norm)
                session.add(
                    JobSkillExtractionSkill(
                        extraction_posting_id=ep.id,
                        raw_skill_name=s["raw_skill_name"],
                        normalized_skill_name=norm,
                        evidence_text=s.get("evidence_text", ""),
                        evidence_type=s.get("evidence_type", "explicit"),
                    )
                )
                n_skill += 1

        session.commit()
        print(f"Imported run {run_key}: {n_post} postings, {n_skill} skill rows.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
