"""Run every remaining step of the July 2026 refresh in one go: import July
postings (no live extraction), apply the reviewed job_skills snapshot,
consolidate near-duplicate skill names, rebuild skill embeddings, and
compute a new (non-canonical) AlignmentRun.

This does NOT promote anything — it stops right before that so the printed
before/after table and run key can be reviewed first. See
pipeline/verify_full_refresh.py and pipeline/promote_run.py for the last step.

The consolidate_skills step (added 2026-07-20) matters every time this
sequence runs, not just for this one refresh: promote_job_skills_v2.py's
own consolidation only clusters at 0.85 cosine similarity, which reliably
merges spelling variants but misses acronym pairs ("NLP" vs "Natural
Language Processing" embeds at 0.60, not 0.85+) and word-subset pairs
("Airflow" vs "Apache Airflow"). Left unmerged, those near-duplicates
silently inflate the "core skill" denominator and create false gaps for
programs that already teach the skill under the other name — see
pipeline/consolidate_skills.py's docstring for the full mechanism. Any
future refresh script (weekly-scrape automation included) should run this
step in the same position: after job_skills is populated, before
build_skill_embeddings.py.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.run_remaining_refresh_steps
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = str(ROOT / ".venv_dashboard" / "bin" / "python")


def run(label: str, args: list[str]) -> str:
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    result = subprocess.run([PYTHON, "-m", *args], cwd=ROOT, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"FAILED at step: {label} (exit {result.returncode})")
    return result.stdout


def main() -> None:
    run("Step A: preview July postings import", ["pipeline.add_july_postings", "--dry-run"])
    run("Step B: import July postings (no live skill extraction)",
        ["pipeline.add_july_postings", "--skip-skill-extraction"])
    run("Step C: preview job_skills snapshot import", ["pipeline.import_job_skills_snapshot", "--dry-run"])
    run("Step D: apply reviewed job_skills snapshot", ["pipeline.import_job_skills_snapshot"])
    run("Step D1: apply job-skill evidence snapshot (Evidence Explorer audit tables)",
        ["pipeline.import_job_skill_evidence"])
    run("Step D2: consolidate near-duplicate skill names", ["pipeline.consolidate_skills"])
    run("Step E: rebuild skill embeddings", ["pipeline.build_skill_embeddings"])
    alignment_output = run("Step F: compute new alignment run", ["pipeline.compute_alignment"])

    run_key = None
    for line in alignment_output.splitlines():
        if "Wrote run '" in line:
            run_key = line.split("Wrote run '")[1].split("'")[0]
    if not run_key:
        raise SystemExit("Could not find the new run key in compute_alignment output — check above.")

    verify_output = run(f"Step G: verify run {run_key}", ["pipeline.verify_full_refresh", "--run-key", run_key])

    print(f"\n{'='*70}")
    print("ALL STEPS DONE. Nothing was promoted.")
    print(f"New run key: {run_key}")
    if "STRUCTURAL CHECKS PASSED" in verify_output:
        print("Verification: STRUCTURAL CHECKS PASSED.")
        print(f"\nIf the before/after table above looks right to you, promote with:")
        print(f"  ./.venv_dashboard/bin/python -m pipeline.promote_run --run-key {run_key}")
    else:
        print("Verification: STRUCTURAL CHECKS FAILED — do NOT promote. Review the output above.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
