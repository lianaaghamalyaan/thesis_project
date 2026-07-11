"""
One-time migration: add a stable job_id to final_jobs_dataset_it_only.csv and
remap job_skills_norm.json from positional integer keys to job_id keys.

Why: dashboard/src/data_loader.py::load_job_skills_by_role() previously joined
job_skills_norm.json (650 entries, keyed "0".."649") to the jobs CSV by row
position (.iloc[idx]). That happened to be correct only because the CSV has
always been appended to, never reordered or deduplicated in place — a fragile
assumption that breaks the moment a scraper run inserts, removes, or resorts
rows. This migration replaces the positional key with a content-derived,
order-independent job_id (sha1 of source_url, which is 100% filled and unique
across all 753 current postings).

Usage:
    python pipeline/migrations/001_stable_job_id.py

Idempotent: safe to re-run. Writes new files; does not delete originals.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOBS_CSV = ROOT / "data/processed/jobs/final_jobs_dataset_it_only.csv"
OLD_SKILLS_JSON = ROOT / "data/processed/unified/job_skills_norm.json"
NEW_SKILLS_JSON = ROOT / "data/processed/unified/job_skills_by_id.json"
JOBS_CSV_WITH_ID = ROOT / "data/processed/jobs/final_jobs_dataset_it_only.csv"


def make_job_id(source_url: str) -> str:
    return hashlib.sha1(source_url.strip().encode("utf-8")).hexdigest()[:16]


def main() -> None:
    import pandas as pd

    df = pd.read_csv(JOBS_CSV)
    if df["source_url"].isna().any():
        missing = df["source_url"].isna().sum()
        print(f"ERROR: {missing} rows have no source_url; cannot derive a stable id for them.", file=sys.stderr)
        sys.exit(1)

    df["job_id"] = df["source_url"].map(make_job_id)
    dupes = df["job_id"].duplicated().sum()
    if dupes:
        print(f"ERROR: {dupes} duplicate job_id values derived — source_url is not unique enough.", file=sys.stderr)
        sys.exit(1)

    if "job_id" in pd.read_csv(JOBS_CSV, nrows=0).columns:
        print(f"{JOBS_CSV.name} already has a job_id column — skipping CSV rewrite.")
    else:
        # job_id first for readability; preserve all existing columns/order after it.
        cols = ["job_id"] + [c for c in df.columns if c != "job_id"]
        df[cols].to_csv(JOBS_CSV_WITH_ID, index=False)
        print(f"Wrote job_id column to {JOBS_CSV_WITH_ID} ({len(df)} rows).")

    if not OLD_SKILLS_JSON.exists():
        print(f"{OLD_SKILLS_JSON} not found — nothing to remap.")
        return

    with open(OLD_SKILLS_JSON) as f:
        positional_skills = json.load(f)

    remapped = {}
    unmapped_positions = []
    for pos_str, skills in positional_skills.items():
        pos = int(pos_str)
        if pos >= len(df):
            unmapped_positions.append(pos)
            continue
        job_id = df.iloc[pos]["job_id"]
        remapped[job_id] = skills

    with open(NEW_SKILLS_JSON, "w") as f:
        json.dump(remapped, f, indent=1, ensure_ascii=False)

    n_total = len(df)
    n_covered = len(remapped)
    print(f"Wrote {NEW_SKILLS_JSON.name}: {n_covered} of {n_total} postings have skill data "
          f"({n_total - n_covered} postings — likely from sources added after the last "
          f"extraction run — still need LLM extraction; see pipeline/extract_job_skills.py).")
    if unmapped_positions:
        print(f"WARNING: {len(unmapped_positions)} positions in the old file had no matching row: {unmapped_positions[:10]}...")


if __name__ == "__main__":
    main()
