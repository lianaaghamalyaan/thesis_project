"""One-time correction: the "Description AI-generated ... no public
description was available from the university" disclosure was attached to
every course_id present in generated_descriptions.json, but 614 of those
1,228 course_ids (nearly all Armenian-language, mostly Yerevan State
University) already had a real, substantial description in the raw CSV —
confirmed 2026-07-13 by comparing generated_ids against the raw
`description` column directly (avg length 1,841 chars, vs. 0 for the six
universities that genuinely never published one). The generation notebook
produced an English rewrite for extraction-consistency reasons, not because
nothing existed; the disclosure text was simply wrong for these courses,
and it made the new documentation-level feature report YSU programs as
"no published data" when the opposite is true.

server/seed.py is fixed for future re-seeds. This script corrects the
`notes` column on an already-seeded DB (local or production) without
touching `description`, `course_skills`, or any score — purely the
disclosure text.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.fix_ai_generated_disclosure
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from .db import SessionLocal

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

AI_NOTE = "Description AI-generated from course name/program context — no public description was available from the university."


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main() -> None:
    generated_ids = set(load_json(PROCESSED / "unified/generated_descriptions.json").keys())
    curriculum = pd.read_csv(PROCESSED / "curriculum/final_curriculum_dataset.csv")
    grouped_curriculum = curriculum.groupby(["university", "program_name", "degree_level"], sort=False)

    session = SessionLocal()
    try:
        rows = session.execute(text("""
            SELECT c.id, u.name AS university, p.name AS program_name, p.degree_level
            FROM courses c
            JOIN program_versions pv ON pv.id = c.program_version_id
            JOIN programs p ON p.id = pv.program_id
            JOIN universities u ON u.id = p.university_id
            WHERE pv.is_current = true
            ORDER BY pv.id, c.id
        """)).all()

        db_course_ids_by_group: dict[tuple, list[int]] = {}
        for db_id, uni, prog, degree in rows:
            db_course_ids_by_group.setdefault((uni, prog, degree), []).append(db_id)

        updates: list[tuple[int, str | None]] = []  # (course_id, notes)
        n_removed_false_positive = 0
        n_skipped_mismatch = 0
        for (uni, prog, degree), csv_rows in grouped_curriculum:
            db_ids = db_course_ids_by_group.get((uni, prog, degree))
            if db_ids is None or len(db_ids) != len(csv_rows):
                n_skipped_mismatch += len(csv_rows)
                continue
            for db_course_id, (_, crow) in zip(db_ids, csv_rows.iterrows()):
                orig_course_id = str(int(crow["course_id"]))
                raw_desc = crow.get("description")
                had_real_raw_description = isinstance(raw_desc, str) and len(raw_desc.strip()) > 50

                notes = crow.get("notes") or None
                notes = pd.notna(notes) and str(notes).strip() or None
                is_generated = orig_course_id in generated_ids and not had_real_raw_description
                if is_generated:
                    notes = f"{notes} {AI_NOTE}" if notes else AI_NOTE
                elif orig_course_id in generated_ids and had_real_raw_description:
                    n_removed_false_positive += 1

                updates.append((db_course_id, notes))

        from psycopg2.extras import execute_values

        raw_conn = session.connection().connection
        with raw_conn.cursor() as cur:
            execute_values(
                cur,
                "UPDATE courses AS c SET notes = v.notes "
                "FROM (VALUES %s) AS v(id, notes) WHERE c.id = v.id",
                updates,
            )
        session.commit()
        print(f"Updated notes for {len(updates)} courses.")
        print(f"  Removed false-positive 'AI-generated / no public description' disclosure from {n_removed_false_positive} courses.")
        if n_skipped_mismatch:
            print(f"  WARNING: skipped {n_skipped_mismatch} courses due to program course-count mismatch.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
