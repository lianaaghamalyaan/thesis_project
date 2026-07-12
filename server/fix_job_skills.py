"""One-time correction: server/seed.py populated job_skills from
job_skills_by_id.json (the raw, per-posting LLM extraction) instead of the
skill-consolidated vocabulary the thesis's actual alignment pipeline used.

The real pipeline (recovered from git history: a7e54d8's
notebooks/03_pipeline/01_run_alignment.ipynb) ran a global 0.85-cosine
clustering pass across every skill source (TF-IDF/KeyBERT/LLM x
curriculum/jobs) BEFORE matching, producing data/processed/unified/
job_skills_norm.json (already-consolidated names) and
skill_consolidation_map.csv (original -> canonical for every phrase that
got merged). Skipping that step is what caused e.g. "Data / ML / AI"
core skills to include unrelated raw-phrase noise and silently
under-reproduce the thesis's published 62.5%/75.5% coverage numbers for
YSU Data Science in Business — confirmed by reproducing that exact number
with the consolidated files.

job_skills_norm.json is row-indexed against a since-deleted file,
data/processed/jobs/final_jobs_dataset_it_with_roles.csv (650 rows, the
original 9-role-category taxonomy from thesis para 146) — also recovered
from git history. This script joins that recovered file back to today's
job_postings table via source_url (537/650 matches; the other 113 were
dropped or changed URL in later re-scrapes and are simply left
un-consolidated, matching current behavior for them).

For postings NOT covered by the historical consolidation (the 113 above,
plus the 103 postings added after the last extraction run), each raw
skill phrase is assigned to its nearest existing canonical concept via the
same 0.85 cosine threshold, falling back to a new canonical entry
(itself) if nothing is close enough — this is exactly what the original
consolidation step did for previously-unseen phrases.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.fix_job_skills
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

from .db import SessionLocal
from .seed import bulk_insert

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CLUSTER_THRESHOLD = 0.85  # matches notebooks/03_pipeline/01_run_alignment.ipynb
RECOVERED_JOBS_WITH_ROLES = ROOT / "data" / "processed" / "jobs" / "_recovered_final_jobs_dataset_it_with_roles.csv"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main() -> None:
    if not RECOVERED_JOBS_WITH_ROLES.exists():
        raise SystemExit(
            f"Missing {RECOVERED_JOBS_WITH_ROLES}. Recover it first: "
            f"git show <initial-commit>:data/processed/jobs/final_jobs_dataset_it_with_roles.csv "
            f"> {RECOVERED_JOBS_WITH_ROLES}"
        )

    old_jobs = pd.read_csv(RECOVERED_JOBS_WITH_ROLES)
    job_skills_norm = load_json(PROCESSED / "unified/job_skills_norm.json")  # row-index -> consolidated skills
    job_skills_raw = load_json(PROCESSED / "unified/job_skills_by_id.json")  # job_id -> raw skills
    consolidation_map = pd.read_csv(PROCESSED / "unified/skill_consolidation_map.csv")
    original_to_canonical = dict(zip(consolidation_map["original"], consolidation_map["canonical"]))

    session = SessionLocal()
    try:
        current_jobs = pd.read_sql(
            text("SELECT id, job_id, source_url FROM job_postings"), session.bind
        )

        merged = (
            old_jobs.reset_index().rename(columns={"index": "old_row_idx"})[["old_row_idx", "source_url"]]
            .merge(current_jobs, on="source_url", how="inner")
        )
        print(f"Matched {len(merged)} / {len(old_jobs)} historically-consolidated postings to current job_postings rows.")

        # posting_id -> consolidated skill list, for matched postings.
        consolidated_by_posting: dict[int, list[str]] = {}
        for _, row in merged.iterrows():
            skills = job_skills_norm.get(str(row["old_row_idx"]))
            if skills is not None:
                consolidated_by_posting[row["id"]] = skills

        matched_posting_ids = set(consolidated_by_posting.keys())
        unmatched = current_jobs[~current_jobs["id"].isin(matched_posting_ids)]
        print(f"{len(unmatched)} postings need on-the-fly consolidation "
              f"(not in the historical 650, or dropped in later re-scrapes).")

        # ── Build the canonical vocabulary from the historical mapping ──
        canonical_vocab = sorted(set(original_to_canonical.values()) | {
            s for skills in job_skills_norm.values() for s in skills
        })

        # ── Collect raw skills for unmatched postings, map through the
        #    historical original->canonical table where an exact hit
        #    exists, and only embed the genuinely novel phrases. ──
        unmatched_raw: dict[int, list[str]] = {}
        novel_phrases: set[str] = set()
        for _, row in unmatched.iterrows():
            raw = job_skills_raw.get(row["job_id"], [])
            unmatched_raw[row["id"]] = raw
            for s in raw:
                if s not in original_to_canonical and s not in canonical_vocab:
                    novel_phrases.add(s)

        skill_map: dict[str, str] = dict(original_to_canonical)
        if novel_phrases:
            print(f"Embedding {len(novel_phrases)} novel phrases + {len(canonical_vocab)} canonical concepts "
                  f"to assign nearest match (cosine >= {CLUSTER_THRESHOLD})...")
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            novel_list = sorted(novel_phrases)
            canon_embs = model.encode(canonical_vocab, batch_size=256, show_progress_bar=False, normalize_embeddings=True)
            novel_embs = model.encode(novel_list, batch_size=256, show_progress_bar=False, normalize_embeddings=True)

            canon_matrix = np.array(canon_embs)
            for i, phrase in enumerate(novel_list):
                sims = canon_matrix @ novel_embs[i]
                best = int(sims.argmax())
                if sims[best] >= CLUSTER_THRESHOLD:
                    skill_map[phrase] = canonical_vocab[best]
                else:
                    skill_map[phrase] = phrase  # becomes its own new canonical concept
                    canonical_vocab.append(phrase)
                    canon_matrix = np.vstack([canon_matrix, novel_embs[i]])

        for posting_id, raw in unmatched_raw.items():
            consolidated_by_posting[posting_id] = sorted({skill_map.get(s, s) for s in raw})

        # ── Rebuild job_skills table ──
        n_deleted = session.execute(text("DELETE FROM job_skills")).rowcount
        print(f"Deleted {n_deleted} existing job_skills rows.")

        new_rows = []
        for posting_id, skills in consolidated_by_posting.items():
            for skill in skills:
                new_rows.append((posting_id, skill, "LLM", "consolidated_v1"))

        bulk_insert(
            session, "job_skills",
            ["posting_id", "skill_name", "extraction_method", "prompt_version"],
            new_rows,
        )
        session.commit()
        print(f"Rebuilt job_skills: {len(consolidated_by_posting)} postings, {len(new_rows)} skill rows.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
