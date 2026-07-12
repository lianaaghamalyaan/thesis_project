"""One-time correction: server/seed.py originally populated course_skills
from course_skills_names_only.json (skills extracted from course titles
only). The canonical experiment is "LLM_desc_semantic" — "desc" means
skills extracted from full course DESCRIPTIONS, a much richer source.
Confirmed empirically 2026-07-12: course_skills_with_desc_norm.json
aggregated per program exactly reproduces the historical n_program_skills
(193 for YSU Data Science in Business vs. only 103 from the names-only
file) — this was a real bug understating every program's skill coverage.

This script deletes and rebuilds ONLY the course_skills table, using the
correct source file, without touching courses/programs/users/passwords/job
data/alignment runs (unlike server/seed.py, which drops and recreates
everything).

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.fix_course_skills
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from .db import SessionLocal
from .models import Course, CourseSkill, ProgramVersion
from .seed import bulk_insert

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    curriculum = pd.read_csv(PROCESSED / "curriculum/final_curriculum_dataset.csv")
    with open(PROCESSED / "unified/course_skills_with_desc_norm.json") as f:
        course_skills = json.load(f)
    with open(PROCESSED / "unified/course_confidence_tiers.json") as f:
        tiers = json.load(f)

    session = SessionLocal()
    try:
        # DB course.id -> original CSV course_id, so we can look up skills.
        # Courses were inserted in the same row order as final_curriculum_dataset.csv
        # (see seed.py::seed_curriculum), grouped by (university, program, degree) —
        # match on that same grouping to rebuild the row-order correspondence.
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

        grouped_curriculum = curriculum.groupby(["university", "program_name", "degree_level"], sort=False)

        db_course_ids_by_group = {}
        for db_id, pv_id, uni, prog, degree in rows:
            db_course_ids_by_group.setdefault((uni, prog, degree), []).append(db_id)

        n_deleted = session.execute(text("DELETE FROM course_skills")).rowcount
        print(f"Deleted {n_deleted} existing course_skills rows.")

        new_rows = []
        n_courses_matched = 0
        for (uni, prog, degree), csv_rows in grouped_curriculum:
            db_ids = db_course_ids_by_group.get((uni, prog, degree))
            if db_ids is None or len(db_ids) != len(csv_rows):
                print(f"  WARNING: course count mismatch for {uni} / {prog} / {degree} "
                      f"(csv={len(csv_rows)}, db={len(db_ids) if db_ids else 0}) — skipping.")
                continue
            for db_course_id, (_, crow) in zip(db_ids, csv_rows.iterrows()):
                orig_course_id = str(int(crow["course_id"]))
                skills = course_skills.get(orig_course_id, [])
                tier_data = tiers.get(orig_course_id, {})
                high_conf = set(tier_data.get("tier1", []))
                for skill in skills:
                    new_rows.append((db_course_id, skill, "high" if skill in high_conf else "low", "LLM", "descriptions"))
                n_courses_matched += 1

        bulk_insert(
            session, "course_skills",
            ["course_id", "skill_name", "confidence_tier", "extraction_method", "input_type"],
            new_rows,
        )
        session.commit()
        print(f"Rebuilt course_skills: {n_courses_matched} courses, {len(new_rows)} skill rows.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
