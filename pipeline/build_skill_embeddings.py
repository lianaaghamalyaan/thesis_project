"""Precompute embeddings for every distinct skill phrase in the database.

Why this exists: the interactive Job Fit feature needs the SAME semantic
matching (cosine >= 0.65, all-MiniLM-L6-v2) as the validated alignment
pipeline — otherwise its numbers contradict the headline scores for the
same program/role pair (observed: 42.9% exact-match vs 62.86% validated
semantic for YSU Data Science in Business vs Data / ML / AI). But the API
server runs on a 512MB instance that cannot load sentence-transformers.
Since every skill is a known string from the consolidated vocabulary, we
embed them all offline here and ship the result as a small npz file
(~5k phrases x 384 dims x float32 ≈ 8MB); the API then does pure-numpy
cosine similarity at request time.

Rerun this whenever new skills enter the DB (new job postings extraction
or curriculum refresh); skills missing from the file fall back to exact
matching in server/analytics.py, so a stale file degrades gracefully
rather than breaking.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.build_skill_embeddings
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / "data" / "processed" / "unified" / "skill_embeddings.npz"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # must match pipeline/compute_alignment.py


def main() -> None:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sqlalchemy import text

    from server.db import SessionLocal

    session = SessionLocal()
    try:
        rows = session.execute(text(
            "SELECT DISTINCT skill_name FROM course_skills "
            "UNION SELECT DISTINCT skill_name FROM job_skills"
        )).all()
    finally:
        session.close()

    vocab = sorted(r[0] for r in rows)
    print(f"Embedding {len(vocab)} distinct skill phrases with {EMBEDDING_MODEL} ...")

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(vocab, show_progress_bar=False, normalize_embeddings=True)

    np.savez_compressed(OUT_PATH, names=np.array(vocab, dtype=object), embeddings=embeddings.astype(np.float32))
    print(f"Saved {OUT_PATH} ({OUT_PATH.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
