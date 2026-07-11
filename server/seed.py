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

# Default local passwords — change before any real deployment. Printed at the
# end of the run so they're not silently lost.
DEFAULT_PASSWORD = "changeme123"


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

    university_by_name: dict[str, University] = {}
    for uni_name in sorted(curriculum["university"].unique()):
        uni = University(name=uni_name, short_name=uni_name.split()[0])
        session.add(uni)
        university_by_name[uni_name] = uni
    session.flush()

    program_id_by_key: dict[tuple[str, str, str], int] = {}
    program_courses: dict[int, list[int]] = {}  # program.id -> [course_id,...] for doc-score calc

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

        course_ids_for_doc_score = []
        for _, crow in rows.iterrows():
            orig_course_id = int(crow["course_id"])
            course = Course(
                program_version_id=version.id,
                course_code=crow.get("course_code") or None,
                name=crow["course_name"],
                name_original=crow.get("course_name_original") or None,
                description=crow.get("description") or None,
                credits=float(crow["credits"]) if pd.notna(crow.get("credits")) else None,
                semester=str(crow["semester"]) if pd.notna(crow.get("semester")) else None,
                source_language=crow.get("source_language") or None,
                source_url=crow.get("source_url") or None,
                notes=crow.get("notes") or None,
            )
            session.add(course)
            session.flush()
            course_ids_for_doc_score.append(orig_course_id)

            skills = course_skills.get(str(orig_course_id), [])
            tier_data = tiers.get(str(orig_course_id), {})
            high_conf = set(tier_data.get("tier1", []))
            for skill in skills:
                session.add(CourseSkill(
                    course_id=course.id,
                    skill_name=skill,
                    confidence_tier="high" if skill in high_conf else "low",
                ))
        program_courses[program.id] = course_ids_for_doc_score

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

    job_id_to_pk: dict[str, int] = {}
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
        session.flush()
        job_id_to_pk[row["job_id"]] = posting.id

        for skill in job_skills_raw.get(row["job_id"], []):
            session.add(JobSkill(
                posting_id=posting.id,
                skill_name=skill,
                extraction_method="LLM",
                prompt_version="thesis_march_2026",
            ))

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
        course_skills = load_json(PROCESSED / "unified/course_skills_names_only.json")
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
