"""Export the job-skill *evidence* audit tables to a job_id-keyed snapshot.

Companion to import_job_skill_evidence.py. The full v2 extraction JSON
(job_skills_v2_20260715.json) is keyed by the extraction-time posting_id —
a positional key that has caused mis-joins before. This writes a stable
snapshot keyed by job_postings.job_id (sha1 of source_url) so the evidence
can be re-applied to ANY database (prod, a fresh clone) without id drift,
exactly like data/processed/unified/job_skills_v2_promoted_snapshot.json
does for the scoring rows.

Run against the database whose job_skill_extraction_* tables are correct
(currently local), then commit the output so import_job_skill_evidence.py
can replay it elsewhere.

    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.export_job_skill_evidence
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.db import SessionLocal  # noqa: E402
from server.models import (  # noqa: E402
    JobPosting,
    JobSkillExtractionPosting,
    JobSkillExtractionRun,
    JobSkillExtractionSkill,
)

OUT_PATH = ROOT / "data/processed/unified/job_skill_evidence_snapshot.json"


def main() -> None:
    session = SessionLocal()
    try:
        run = (
            session.query(JobSkillExtractionRun)
            .filter(JobSkillExtractionRun.status == "completed")
            .order_by(JobSkillExtractionRun.created_at.desc())
            .first()
        )
        if run is None:
            raise SystemExit("No completed extraction run to export.")

        pid_to_jobid = dict(session.query(JobPosting.id, JobPosting.job_id).all())

        rows = (
            session.query(JobSkillExtractionPosting, JobSkillExtractionSkill)
            .join(JobSkillExtractionSkill, JobSkillExtractionSkill.extraction_posting_id == JobSkillExtractionPosting.id)
            .filter(JobSkillExtractionPosting.run_id == run.id)
            .all()
        )
        by_job: dict[str, list[dict]] = {}
        for ep, sk in rows:
            job_id = pid_to_jobid.get(ep.posting_id)
            if not job_id:
                continue
            by_job.setdefault(job_id, []).append(
                {
                    "raw_skill_name": sk.raw_skill_name,
                    "normalized_skill_name": sk.normalized_skill_name,
                    "evidence_text": sk.evidence_text,
                    "evidence_type": sk.evidence_type,
                }
            )

        payload = {
            "run": {
                "run_key": run.run_key,
                "model_name": run.model_name,
                "prompt_version": run.prompt_version,
                "expected_postings": run.expected_postings,
            },
            "by_job_id": by_job,
        }
        OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False))
        print(
            f"Wrote {OUT_PATH.relative_to(ROOT)} — run {run.run_key}, "
            f"{len(by_job)} postings, {sum(len(v) for v in by_job.values())} skill rows."
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
