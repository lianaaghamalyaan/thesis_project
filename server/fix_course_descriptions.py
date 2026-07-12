"""One-time correction: server/seed.py populated courses.description from
the raw curriculum CSV's `description` column, which is genuinely empty for
6 of 8 universities (National Polytechnic University of Armenia, National
University of Architecture and Construction of Armenia, Russian-Armenian
University, Université Française en Arménie, Armenian State University of
Economics, Armenian State Pedagogical University) — confirmed 2026-07-12 by
checking each university's actual public curriculum page/PDF/document
directly, not a scraper gap, these institutions simply don't publish
per-course descriptions anywhere public. pandas' NaN got stored as the
literal string "NaN" in the DB for ~599 courses.

This is a purely cosmetic/reporting bug, NOT a scoring bug: skill
extraction (course_skills_with_desc_norm.json) already used
data/processed/unified/best_descriptions.json — real descriptions where
they exist (YSU, AUA), LLM-generated ones (from course name + program
context, via notebooks/02_extraction/llm/generate_descriptions.ipynb,
recovered from git history) everywhere else — so alignment scores were
never affected. What needs fixing is just the DB's description/notes text
so the Admin "missing descriptions" report and any description display
stop showing literal "NaN" and instead show the real content, with AI-
generated ones clearly disclosed via a notes suffix.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.fix_course_descriptions
"""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text

from .db import SessionLocal
from .models import Course, ProgramVersion

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

AI_NOTE = "Description AI-generated from course name/program context — no public description was available from the university."


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main() -> None:
    best_descriptions = load_json(PROCESSED / "unified/best_descriptions.json")
    generated_ids = set(load_json(PROCESSED / "unified/generated_descriptions.json").keys())

    session = SessionLocal()
    try:
        import pandas as pd

        curriculum = pd.read_csv(PROCESSED / "curriculum/final_curriculum_dataset.csv")
        grouped_curriculum = curriculum.groupby(["university", "program_name", "degree_level"], sort=False)

        rows = session.execute(text("""
            SELECT c.id, pv.id AS program_version_id, u.name AS university,
                   p.name AS program_name, p.degree_level
            FROM courses c
            JOIN program_versions pv ON pv.id = c.program_version_id
            JOIN programs p ON p.id = pv.program_id
            JOIN universities u ON u.id = p.university_id
            WHERE pv.is_current = true
            ORDER BY pv.id, c.id
        """)).all()

        db_course_ids_by_group: dict[tuple, list[int]] = {}
        for db_id, pv_id, uni, prog, degree in rows:
            db_course_ids_by_group.setdefault((uni, prog, degree), []).append(db_id)

        updates: list[tuple[int, str, str | None]] = []  # (course_id, description, notes)
        n_skipped_mismatch = 0
        for (uni, prog, degree), csv_rows in grouped_curriculum:
            db_ids = db_course_ids_by_group.get((uni, prog, degree))
            if db_ids is None or len(db_ids) != len(csv_rows):
                n_skipped_mismatch += len(csv_rows)
                continue
            for db_course_id, (_, crow) in zip(db_ids, csv_rows.iterrows()):
                orig_course_id = str(int(crow["course_id"]))
                description = best_descriptions.get(orig_course_id)
                if not description:
                    continue
                notes = crow.get("notes") or None
                notes = pd.notna(notes) and str(notes).strip() or None
                if orig_course_id in generated_ids:
                    notes = f"{notes} {AI_NOTE}" if notes else AI_NOTE
                updates.append((db_course_id, description, notes))

        # Single batched UPDATE ... FROM (VALUES ...) via execute_values,
        # instead of one round trip per row — 1,545 individual UPDATEs over
        # a remote connection hung for 15+ minutes before this fix (same
        # class of bug documented in server/seed.py's bulk_insert()).
        from psycopg2.extras import execute_values

        raw_conn = session.connection().connection
        with raw_conn.cursor() as cur:
            execute_values(
                cur,
                "UPDATE courses AS c SET description = v.description, notes = v.notes "
                "FROM (VALUES %s) AS v(id, description, notes) WHERE c.id = v.id",
                updates,
            )
        session.commit()
        print(f"Updated descriptions for {len(updates)} courses.")
        if n_skipped_mismatch:
            print(f"  WARNING: skipped {n_skipped_mismatch} courses due to program course-count mismatch.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
