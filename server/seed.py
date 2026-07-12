"""One-time (idempotent) migration: load all processed CSV/JSON data into the
database defined in server/models.py.

Usage:
    ./.venv_dashboard/bin/python -m server.seed

Safe to re-run: truncates and reloads every table it manages. This is the
"thesis snapshot becomes run #1" migration described in
docs/product/data_pipeline_architecture.md and system_architecture_plan.md §6.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from psycopg2.extras import execute_values

from .auth import hash_password
from .db import SessionLocal, engine
from .models import (
    AlignmentResult,
    AlignmentRun,
    Base,
    Course,
    CourseSkill,
    GapSkill,
    JobCollection,
    JobPosting,
    JobSkill,
    JobSource,
    Organization,
    Program,
    ProgramVersion,
    University,
    User,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CANONICAL_EXPERIMENT = "LLM_desc_semantic"
CURRICULUM_COLLECTED_AT = date(2026, 3, 20)
JOB_SNAPSHOT_DATE = date(2026, 3, 20)
RUN_KEY = "march_2026_static"

# Default local passwords. This script drops and recreates every table it
# manages (including users), so re-running seed.py against a live database
# WILL reset all passwords back to this value — always run
# server/reset_passwords.py again immediately after any re-seed of a
# database anyone outside development can reach.
DEFAULT_PASSWORD = "changeme123"


def bulk_insert(session, table_name: str, columns: list[str], rows: list[tuple]) -> None:
    """Bulk-insert via psycopg2.extras.execute_values on the same connection
    (and transaction) as the ORM session — session.commit()/rollback() still
    covers these rows.

    Used instead of the ORM for CourseSkill/JobSkill (8,298 + 5,137 rows):
    neither table's generated id is referenced afterward, so there's no need
    for RETURNING. That matters because SQLAlchemy 2.0's ORM bulk-insert path
    (insertmanyvalues, used automatically once >1 row is pending at flush())
    combined with RETURNING hit a real bug against this schema — a FLOAT
    column (Course.credits) sitting next to a VARCHAR column of similarly
    formatted values (Course.semester, e.g. "1.0") caused Postgres to receive
    a value in the wrong column position ("invalid input syntax for type
    double precision: 'Թուրքերեն-2'"), reproduced consistently both locally
    and against Supabase. Root-causing that further wasn't worth the time
    against a one-time migration script; execute_values sidesteps it (and is
    also just plain faster over a slow network — one round trip per page
    instead of one per row, without needing use_insertmanyvalues at all).
    """
    if not rows:
        return
    raw_conn = session.connection().connection
    with raw_conn.cursor() as cur:
        col_list = ", ".join(columns)
        execute_values(cur, f"INSERT INTO {table_name} ({col_list}) VALUES %s", rows, page_size=500)


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def doc_score_and_gap_type(course_ids: list[int], tiers: dict) -> tuple[float, str]:
    total_tier1 = total_combined = 0
    for cid in course_ids:
        t = tiers.get(str(cid), {})
        total_tier1 += len(t.get("tier1", []))
        total_combined += len(t.get("combined", []))
    if total_combined == 0:
        return 0.0, "uncertain"
    score = total_tier1 / total_combined
    if score >= 0.45:
        return score, "curriculum_gap"
    if score <= 0.20:
        return score, "documentation_gap"
    return score, "uncertain"


def seed_curriculum(session, course_skills: dict, tiers: dict) -> dict[tuple[str, str, str], int]:
    """Returns {(university, program, degree): program_id}."""
    curriculum = pd.read_csv(PROCESSED / "curriculum/final_curriculum_dataset.csv")
    role_map = load_json(PROCESSED / "role_aware/program_role_mapping.json")
    # 6 of 8 universities (NPUA, NUACA, RAU, UFAR, ASUE, ASPU) never had real
    # course descriptions published anywhere public (confirmed 2026-07-12 by
    # checking each university's actual curriculum page/PDF/doc directly —
    # not a scraper gap, the institutions simply don't publish per-course
    # syllabi). notebooks/02_extraction/llm/generate_descriptions.ipynb
    # (recovered from git history) already solved this by LLM-generating a
    # short description from course name + program context for every course
    # lacking one, and course_skills_with_desc_norm.json's skill extraction
    # already used this file — the alignment SCORES were never affected by
    # this gap. What WAS broken: seed.py used the raw CSV `description`
    # column here instead, so the DB stored literal "NaN" for ~599 courses
    # (a purely cosmetic/reporting bug — see server/fix_course_descriptions.py
    # for the non-destructive correction of an already-seeded DB).
    best_descriptions = load_json(PROCESSED / "unified/best_descriptions.json")
    generated_ids = set(load_json(PROCESSED / "unified/generated_descriptions.json").keys())

    university_by_name: dict[str, University] = {}
    for uni_name in sorted(curriculum["university"].unique()):
        uni = University(name=uni_name, short_name=uni_name.split()[0])
        session.add(uni)
        university_by_name[uni_name] = uni
    session.flush()

    program_id_by_key: dict[tuple[str, str, str], int] = {}
    program_courses: dict[int, list[int]] = {}  # program.id -> [course_id,...] for doc-score calc
    all_course_skill_rows: list[tuple] = []  # accumulated for one bulk_insert at the end

    grouped = curriculum.groupby(["university", "program_name", "degree_level"], sort=False)
    for (uni_name, prog_name, degree), rows in grouped:
        role_key = f"{uni_name} | {prog_name} | {degree}"
        raw_roles = role_map.get(role_key)
        # program_role_mapping.json stores role lists as JSON arrays (e.g.
        # ["Data / ML / AI"]) or the literal string "ALL"; downstream code
        # (formatting.roles_display, benchmark._roles_overlap) expects a
        # single comma-joined string, matching alignment_results.csv's shape.
        if isinstance(raw_roles, list):
            relevant_roles = ", ".join(raw_roles)
        else:
            relevant_roles = raw_roles
        # Every program's courses share one curriculum-page URL in this
        # dataset (verified: 0 of 44 programs have >1 distinct source_url
        # among their courses) — that shared URL is the refresh target for
        # the 6-month curriculum recollection job.
        program_source_urls = rows["source_url"].dropna().unique()
        program_source_url = program_source_urls[0] if len(program_source_urls) else None

        program = Program(
            university_id=university_by_name[uni_name].id,
            name=prog_name,
            degree_level=degree,
            relevant_roles=relevant_roles,
            source_url=program_source_url,
        )
        session.add(program)
        session.flush()
        program_id_by_key[(uni_name, prog_name, degree)] = program.id

        version = ProgramVersion(
            program_id=program.id,
            version_number=1,
            collected_at=CURRICULUM_COLLECTED_AT,
            is_current=True,
            notes="Migrated from thesis March 2026 snapshot",
        )
        session.add(version)
        session.flush()

        # Build all of this program's Course rows first and flush ONCE
        # (rather than after every course) — over a remote DB, one
        # round-trip per row for ~1,545 courses made this migration
        # effectively hang (14+ minutes with nothing committed). SQLAlchemy
        # assigns .id to every pending object in a single flush, so this
        # batching is free correctness-wise, just far fewer round trips.
        course_ids_for_doc_score = []
        courses_batch = []
        for _, crow in rows.iterrows():
            orig_course_id = int(crow["course_id"])
            course_id_str = str(orig_course_id)
            description = best_descriptions.get(course_id_str) or crow.get("description") or None
            notes = crow.get("notes") or None
            if course_id_str in generated_ids:
                ai_note = "Description AI-generated from course name/program context — no public description was available from the university."
                notes = f"{notes} {ai_note}" if notes else ai_note
            course = Course(
                program_version_id=version.id,
                course_code=crow.get("course_code") or None,
                name=crow["course_name"],
                name_original=crow.get("course_name_original") or None,
                description=description,
                credits=float(crow["credits"]) if pd.notna(crow.get("credits")) else None,
                semester=str(crow["semester"]) if pd.notna(crow.get("semester")) else None,
                source_language=crow.get("source_language") or None,
                source_url=crow.get("source_url") or None,
                notes=notes,
            )
            session.add(course)
            courses_batch.append((course, orig_course_id))
            course_ids_for_doc_score.append(orig_course_id)
        session.flush()

        for course, orig_course_id in courses_batch:
            skills = course_skills.get(str(orig_course_id), [])
            tier_data = tiers.get(str(orig_course_id), {})
            high_conf = set(tier_data.get("tier1", []))
            for skill in skills:
                all_course_skill_rows.append((
                    course.id, skill, "high" if skill in high_conf else "low", "LLM", "names",
                ))
        program_courses[program.id] = course_ids_for_doc_score

    bulk_insert(
        session, "course_skills",
        ["course_id", "skill_name", "confidence_tier", "extraction_method", "input_type"],
        all_course_skill_rows,
    )

    session.commit()
    return program_id_by_key, program_courses, tiers


def seed_jobs(session) -> dict[str, int]:
    """Returns {job_id: posting_row_id}."""
    jobs = pd.read_csv(PROCESSED / "jobs/final_jobs_dataset_it_only.csv")
    job_skills_raw = load_json(PROCESSED / "unified/job_skills_by_id.json")

    source_by_name: dict[str, JobSource] = {}
    for src_name in sorted(jobs["source"].unique()):
        src = JobSource(name=src_name, source_type="aggregator" if src_name in ("job.am", "staff.am", "myjob.am", "linkedin") else "company_portal")
        session.add(src)
        source_by_name[src_name] = src
    session.flush()

    counts_by_source = jobs["source"].value_counts()
    for src_name, count in counts_by_source.items():
        session.add(JobCollection(
            source_id=source_by_name[src_name].id,
            n_collected=int(count),
            n_new=int(count),
            status="success",
            notes="Migrated from thesis March 2026 snapshot",
        ))

    # Same batching fix as seed_curriculum: build all postings first, flush
    # once (not once per row), then attach skills using the now-populated ids.
    job_id_to_pk: dict[str, int] = {}
    postings_batch = []
    for _, row in jobs.iterrows():
        posting_date = pd.to_datetime(row["posting_date"], errors="coerce")
        deadline = pd.to_datetime(row.get("deadline"), errors="coerce")
        posting = JobPosting(
            job_id=row["job_id"],
            source_id=source_by_name[row["source"]].id,
            source_url=row["source_url"],
            title=row["job_title"],
            company_name=row.get("company_name") or None,
            location=row.get("location") or None,
            employment_type=row.get("employment_type") or None,
            seniority_level=row.get("seniority_level") or None,
            posting_date=posting_date.date() if pd.notna(posting_date) else None,
            deadline=deadline.date() if pd.notna(deadline) else None,
            full_text=row.get("full_text") or None,
            is_it_job=True,
            it_role_group=row.get("it_role_group") or None,
            first_seen_at=datetime.combine(JOB_SNAPSHOT_DATE, datetime.min.time()),
            last_seen_at=datetime.combine(JOB_SNAPSHOT_DATE, datetime.min.time()),
            is_active=True,
        )
        session.add(posting)
        postings_batch.append((posting, row["job_id"]))
    session.flush()

    job_skill_rows: list[tuple] = []
    for posting, job_id in postings_batch:
        job_id_to_pk[job_id] = posting.id
        for skill in job_skills_raw.get(job_id, []):
            job_skill_rows.append((posting.id, skill, "LLM", "thesis_march_2026"))

    bulk_insert(
        session, "job_skills",
        ["posting_id", "skill_name", "extraction_method", "prompt_version"],
        job_skill_rows,
    )

    session.commit()
    return job_id_to_pk


def seed_alignment(session, program_id_by_key, program_courses, tiers):
    alignment = pd.read_csv(PROCESSED / "unified/alignment_results.csv")
    alignment = alignment[alignment["experiment"] == CANONICAL_EXPERIMENT]

    llm_gaps = pd.read_csv(PROCESSED / "llm_skills/llm_gap_analysis.csv")
    fallback_gaps = pd.read_csv(PROCESSED / "unified/gap_analysis.csv")

    run = AlignmentRun(
        run_key=RUN_KEY,
        experiment=CANONICAL_EXPERIMENT,
        esco_version="v1.2",
        job_snapshot_date=JOB_SNAPSHOT_DATE,
        n_active_postings=753,
        is_canonical=True,
        status="complete",
        notes="Thesis research snapshot, migrated 2026-07-11. Not yet reproducible from a runnable pipeline (see system_architecture_plan.md Stage A blocker).",
    )
    session.add(run)
    session.flush()

    for _, row in alignment.iterrows():
        key = (row["university"], row["program"], row["degree"])
        program_id = program_id_by_key.get(key)
        if program_id is None:
            continue

        def f(col):
            v = row.get(col)
            return float(v) if pd.notna(v) else None

        def i(col):
            v = row.get(col)
            return int(v) if pd.notna(v) else None

        result = AlignmentResult(
            run_id=run.id,
            program_id=program_id,
            n_program_skills=i("n_program_skills"),
            n_job_skills=i("n_job_skills"),
            n_overlap=i("n_overlap"),
            full_coverage_pct=f("full_coverage_pct"),
            role_coverage_pct=f("role_coverage_pct"),
            core_role_coverage_pct=f("core_role_coverage_pct"),
            core_n_job_skills=i("core_n_job_skills"),
            core_n_overlap=i("core_n_overlap"),
            core_n_gap=i("core_n_gap"),
            weighted_core_coverage_pct=f("weighted_core_coverage_pct"),
        )
        session.add(result)
        session.flush()

        _, gap_type = doc_score_and_gap_type(program_courses.get(program_id, []), tiers)

        prog_llm_gaps = llm_gaps[
            (llm_gaps["university"] == row["university"])
            & (llm_gaps["program_name"] == row["program"])
            & (llm_gaps["degree_level"] == row["degree"])
        ]
        if not prog_llm_gaps.empty:
            for _, g in prog_llm_gaps.iterrows():
                session.add(GapSkill(
                    result_id=result.id,
                    skill_name=g["missing_skill"],
                    job_frequency=int(g["job_frequency"]) if pd.notna(g["job_frequency"]) else None,
                    category=g.get("category") or None,
                    gap_type=gap_type,
                ))
        else:
            prog_gaps = fallback_gaps[
                (fallback_gaps["university"] == row["university"])
                & (fallback_gaps["program"] == row["program"])
                & (fallback_gaps["degree"] == row["degree"])
            ]
            for _, g in prog_gaps.iterrows():
                session.add(GapSkill(
                    result_id=result.id,
                    skill_name=g["gap_skill"],
                    job_frequency=int(g["job_frequency"]) if pd.notna(g["job_frequency"]) else None,
                    gap_type=gap_type,
                ))

    session.commit()


def seed_accounts(session):
    """One org+user per university, plus a policy demo org and a superadmin."""
    created_logins = []

    internal_org = Organization(name="CurriculumLens Operations", org_type="internal")
    session.add(internal_org)
    session.flush()
    superadmin = User(
        email="admin@curriculumlens.local",
        password_hash=hash_password(DEFAULT_PASSWORD),
        full_name="Platform Admin",
        role="superadmin",
        organization_id=internal_org.id,
    )
    session.add(superadmin)
    created_logins.append(("admin@curriculumlens.local", DEFAULT_PASSWORD, "superadmin — sees everything"))

    policy_org = Organization(name="Ministry of Education Demo", org_type="policy")
    session.add(policy_org)
    session.flush()
    policy_user = User(
        email="policy-demo@curriculumlens.local",
        password_hash=hash_password(DEFAULT_PASSWORD),
        full_name="Policy Viewer (Demo)",
        role="viewer",
        organization_id=policy_org.id,
    )
    session.add(policy_user)
    created_logins.append(("policy-demo@curriculumlens.local", DEFAULT_PASSWORD, "policy — sees all universities, named"))

    universities = session.query(University).all()
    used_slugs: set[str] = set()
    for uni in universities:
        # Acronym from the full name (e.g. "Yerevan State University" -> "ysu")
        # is far less collision-prone than the first word alone (two
        # "Armenian State ..." universities share that first word).
        acronym = "".join(w[0] for w in uni.name.split() if w[0].isalpha()).lower()
        slug = acronym or f"uni{uni.id}"
        if slug in used_slugs:
            slug = f"{slug}{uni.id}"
        used_slugs.add(slug)

        org = Organization(name=f"{uni.name} (University Account)", org_type="university", university_id=uni.id)
        session.add(org)
        session.flush()
        user = User(
            email=f"{slug}@curriculumlens.local",
            password_hash=hash_password(DEFAULT_PASSWORD),
            full_name=f"{uni.name} Admin",
            role="org_admin",
            organization_id=org.id,
        )
        session.add(user)
        created_logins.append((f"{slug}@curriculumlens.local", DEFAULT_PASSWORD, f"university — sees only {uni.name}"))

    session.commit()
    return created_logins


def main():
    print(f"Creating tables on {engine.url.database!r} ...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        print("Loading course skills / confidence tiers ...")
        # CANONICAL_EXPERIMENT is "LLM_desc_semantic" — "desc" means skills
        # extracted from full course DESCRIPTIONS, not just course names.
        # Confirmed empirically 2026-07-12: course_skills_with_desc_norm.json
        # aggregated per program reproduces the historical n_program_skills
        # exactly (193 for YSU Data Science in Business); the names_only file
        # (used here previously) gives only 103 — a real bug that understated
        # every program's skill coverage in this database until this fix.
        course_skills = load_json(PROCESSED / "unified/course_skills_with_desc_norm.json")
        tiers = load_json(PROCESSED / "unified/course_confidence_tiers.json")

        print("Seeding universities, programs, courses, course skills ...")
        program_id_by_key, program_courses, tiers = seed_curriculum(session, course_skills, tiers)
        print(f"  {len(program_id_by_key)} programs")

        print("Seeding job sources, postings, job skills ...")
        job_id_to_pk = seed_jobs(session)
        print(f"  {len(job_id_to_pk)} postings")

        print("Seeding alignment run, results, gap skills ...")
        seed_alignment(session, program_id_by_key, program_courses, tiers)

        print("Seeding organizations and users ...")
        logins = seed_accounts(session)

        print("\nDone. Login credentials (change DEFAULT_PASSWORD before real deployment):")
        for email, pw, desc in logins:
            print(f"  {email}  /  {pw}   [{desc}]")
    finally:
        session.close()


if __name__ == "__main__":
    main()
