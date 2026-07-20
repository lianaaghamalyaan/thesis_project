"""Import fresh scraper output (data/raw/jobs/*.csv, written by
pipeline/run_collection.py) into JobPosting rows: classify each posting with
pipeline/it_classifier.py, insert genuinely new postings that classify as
"keep", bump last_seen_at for postings already in the database, write
"review"-decision postings to a CSV for manual judgment instead of guessing,
and mark postings unseen for INACTIVE_AFTER_DAYS as inactive (CLAUDE.md's
"old postings should be marked inactive, not deleted").

This is the general, always-runnable successor to pipeline/add_july_postings.py
(which was hardcoded to one specific dated refresh's file paths and a fixed
source list) — this script works from whatever's currently in data/raw/jobs/
and whatever sources currently exist in job_sources (creating a new one, not
failing, if a scraper writes a source name the DB hasn't seen before).

Does NOT extract skills — that's pipeline/extract_new_postings_skills.py,
run afterward, scoped to only the postings this script actually inserted.
Does NOT touch compute_alignment.py or promote_run.py.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.import_new_postings [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw" / "jobs"
REVIEW_QUEUE_CSV = ROOT / "data" / "processed" / "jobs" / "latest_review_queue.csv"
INACTIVE_AFTER_DAYS = 180

# CSV `source` column values that differ from the job_sources.name they map
# to (punctuation/casing only — everything else passes through unchanged).
SOURCE_NAME_MAP = {
    "jobam": "job.am",
    "staffam": "staff.am",
    "10web": "10web",
}


def make_job_id(source_url: str) -> str:
    return hashlib.sha1(source_url.strip().encode("utf-8")).hexdigest()[:16]


def load_raw_postings() -> pd.DataFrame:
    frames = []
    for csv_path in sorted(RAW_DIR.glob("*.csv")):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:  # noqa: BLE001 - a malformed scraper CSV shouldn't kill the whole import
            print(f"  WARNING: could not read {csv_path.name}: {e}", file=sys.stderr)
            continue
        if "source_url" not in df.columns:
            print(f"  WARNING: {csv_path.name} has no source_url column, skipping.", file=sys.stderr)
            continue
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["source_url"])
    combined["job_id"] = combined["source_url"].map(make_job_id)
    before = len(combined)
    combined = combined.drop_duplicates(subset="job_id", keep="first")
    if before != len(combined):
        print(f"  Dropped {before - len(combined)} duplicate source_url rows across raw CSVs.")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from pipeline.it_classifier import classify_job
    from server.db import SessionLocal
    from server.models import JobPosting, JobSource

    df = load_raw_postings()
    if df.empty:
        print("No raw postings found in data/raw/jobs/ — nothing to do.")
        return
    print(f"{len(df)} distinct postings across all raw scraper CSVs.")

    session = SessionLocal()
    try:
        existing_job_ids = {row[0] for row in session.query(JobPosting.job_id).all()}
        new_df = df[~df["job_id"].isin(existing_job_ids)]
        overlap_ids = set(df["job_id"]) & existing_job_ids
        print(f"  {len(overlap_ids)} already exist as JobPosting rows — will bump last_seen_at, not duplicate.")
        print(f"  {len(new_df)} are genuinely new — classifying ...")

        decisions = new_df.apply(
            lambda row: classify_job(row.get("job_title", ""), row.get("full_text", "")), axis=1
        )
        new_df = new_df.assign(
            it_filter_decision=[d[0] for d in decisions],
            it_role_group=[d[1] for d in decisions],
            it_filter_reason=[d[2] for d in decisions],
            it_tech_text_score=[d[3] for d in decisions],
        )
        counts = new_df["it_filter_decision"].value_counts()
        for decision, count in counts.items():
            print(f"    {decision}: {count}")

        keep_df = new_df[new_df["it_filter_decision"] == "keep"]
        review_df = new_df[new_df["it_filter_decision"] == "review"]

        if not review_df.empty:
            REVIEW_QUEUE_CSV.parent.mkdir(parents=True, exist_ok=True)
            review_df.to_csv(REVIEW_QUEUE_CSV, index=False)
            print(f"  {len(review_df)} postings need a human decision — written to "
                  f"{REVIEW_QUEUE_CSV.relative_to(ROOT)} (not imported; re-run after manually promoting any "
                  "of these into a raw CSV with a clear IT title, or just leave them out).")

        if args.dry_run:
            print(f"\nDry run — no writes. Would insert {len(keep_df)} new postings, "
                  f"bump last_seen_at on {len(overlap_ids)}.")
            if len(keep_df):
                print(keep_df[["job_id", "source", "job_title", "company_name"]].head(10).to_string(index=False))
            return

        sources = {s.name: s for s in session.query(JobSource).all()}
        for raw_name in keep_df["source"].dropna().unique():
            mapped = SOURCE_NAME_MAP.get(raw_name, raw_name)
            if mapped not in sources:
                new_source = JobSource(name=mapped, source_type="company_portal")
                session.add(new_source)
                session.flush()
                sources[mapped] = new_source
                print(f"  Created new job_sources row for {mapped!r} (first time seeing this source).")

        if overlap_ids:
            session.query(JobPosting).filter(JobPosting.job_id.in_(overlap_ids)).update(
                {"last_seen_at": datetime.utcnow()}, synchronize_session=False
            )

        n_inserted = 0
        for _, row in keep_df.iterrows():
            mapped_source = SOURCE_NAME_MAP.get(row["source"], row["source"])
            posting_date = pd.to_datetime(row.get("posting_date"), errors="coerce")
            session.add(JobPosting(
                job_id=row["job_id"],
                source_id=sources[mapped_source].id,
                source_url=row["source_url"],
                title=str(row.get("job_title", ""))[:500],
                company_name=(row.get("company_name") or None),
                location=(row.get("location") or None),
                seniority_level=(row.get("seniority_level") or None),
                posting_date=posting_date.date() if pd.notna(posting_date) else None,
                full_text=row.get("full_text"),
                is_it_job=True,
                it_role_group=row["it_role_group"],
                is_active=True,
            ))
            n_inserted += 1

        # CLAUDE.md: "old postings should be marked inactive, not deleted."
        cutoff = datetime.utcnow() - timedelta(days=INACTIVE_AFTER_DAYS)
        n_deactivated = (
            session.query(JobPosting)
            .filter(JobPosting.is_active == True, JobPosting.last_seen_at < cutoff)  # noqa: E712
            .update({"is_active": False}, synchronize_session=False)
        )

        session.commit()
        print(f"\nInserted {n_inserted} new postings. Bumped last_seen_at on {len(overlap_ids)}. "
              f"Deactivated {n_deactivated} postings unseen for {INACTIVE_AFTER_DAYS}+ days.")
        print("Next: pipeline.extract_new_postings_skills, then pipeline.consolidate_skills, "
              "pipeline.build_skill_embeddings, pipeline.compute_alignment.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
