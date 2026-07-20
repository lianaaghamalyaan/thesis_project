"""Read queries used by the dashboard. Every function returns the same shape
as the old CSV-based dashboard/src/data_loader.py so pages don't need to
change — only what feeds them does (DB instead of flat files).

Visibility rule (system_architecture_plan.md §9): a `university` filter of
None means "all universities" — only policy/superadmin views may request
that. University accounts always pass their own university name.
"""
from __future__ import annotations

from collections import Counter

import pandas as pd
from sqlalchemy import select

from .db import get_session
from .models import (
    AlignmentResult,
    AlignmentRun,
    Course,
    CourseSkill,
    GapSkill,
    JobCollection,
    JobPosting,
    JobSkill,
    JobSource,
    Program,
    ProgramOutcome,
    ProgramOutcomeSkill,
    ProgramVersion,
    University,
)

CANONICAL_EXPERIMENT = "LLM_desc_semantic"


def list_universities() -> list[str]:
    session = get_session()
    try:
        return [u.name for u in session.query(University).order_by(University.name).all()]
    finally:
        session.close()


def _canonical_run(session) -> AlignmentRun | None:
    return session.query(AlignmentRun).filter(AlignmentRun.is_canonical == True).first()  # noqa: E712


def load_curriculum(university: str | None) -> pd.DataFrame:
    """Matches the shape of final_curriculum_dataset.csv (current program version only)."""
    session = get_session()
    try:
        q = (
            select(Course, Program, University, ProgramVersion)
            .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(ProgramVersion.is_current == True)  # noqa: E712
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        records = []
        for course, program, uni, version in rows:
            records.append({
                "course_id": course.id,
                "university": uni.name,
                "program_name": program.name,
                "degree_level": program.degree_level,
                "course_code": course.course_code,
                "course_name": course.name,
                "course_name_original": course.name_original,
                "credits": course.credits,
                "semester": course.semester,
                "description": course.description,
                "source_language": course.source_language,
                "notes": course.notes,
                "source_url": course.source_url,
                "academic_year": version.academic_year,
            })
        return pd.DataFrame.from_records(records)
    finally:
        session.close()


def load_alignment(university: str | None) -> pd.DataFrame:
    """Matches alignment_results.csv shape, filtered to the canonical run."""
    session = get_session()
    try:
        run = _canonical_run(session)
        if run is None:
            return pd.DataFrame()
        q = (
            select(AlignmentResult, Program, University)
            .join(Program, AlignmentResult.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(AlignmentResult.run_id == run.id)
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        records = []
        for result, program, uni in rows:
            records.append({
                "experiment": run.experiment,
                "university": uni.name,
                "program": program.name,
                "degree": program.degree_level,
                "relevant_roles": program.relevant_roles,
                "source_url": program.source_url,
                "n_program_skills": result.n_program_skills,
                "n_job_skills": result.n_job_skills,
                "n_overlap": result.n_overlap,
                "full_coverage_pct": result.full_coverage_pct,
                "role_coverage_pct": result.role_coverage_pct,
                "core_role_coverage_pct": result.core_role_coverage_pct,
                "core_n_job_skills": result.core_n_job_skills,
                "core_n_overlap": result.core_n_overlap,
                "core_n_gap": result.core_n_gap,
                "weighted_core_coverage_pct": result.weighted_core_coverage_pct,
                "_result_id": result.id,
            })
        return pd.DataFrame.from_records(records)
    finally:
        session.close()


def load_gaps(university: str | None) -> pd.DataFrame:
    """Matches gap_analysis.csv shape (flat, no category)."""
    session = get_session()
    try:
        run = _canonical_run(session)
        if run is None:
            return pd.DataFrame()
        q = (
            select(GapSkill, Program, University)
            .join(AlignmentResult, GapSkill.result_id == AlignmentResult.id)
            .join(Program, AlignmentResult.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(AlignmentResult.run_id == run.id)
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        records = [{
            "university": uni.name,
            "program": program.name,
            "degree": program.degree_level,
            "gap_skill": gap.skill_name,
            "job_frequency": gap.job_frequency,
            "relevant_roles": program.relevant_roles,
        } for gap, program, uni in rows]
        return pd.DataFrame.from_records(records)
    finally:
        session.close()


_LLM_GAPS_COLUMNS = ["university", "program_name", "degree_level", "role_groups", "missing_skill", "job_frequency", "category"]


def load_llm_gaps(university: str | None) -> pd.DataFrame:
    """Matches llm_gap_analysis.csv shape (has category). Only the frozen
    March 2026 snapshot has per-skill categories (LLM-classified as part of
    the original thesis pipeline); live-recomputed runs (pipeline/
    compute_alignment.py) don't classify categories, so this legitimately
    returns zero rows for those — callers fall back to load_gaps() /
    load_llm_gaps()'s "role_groups"-less sibling in that case. Always
    returns the expected columns (even when empty) so
    `df["some_column"]` boolean-indexing in callers doesn't KeyError on an
    empty, columnless DataFrame."""
    session = get_session()
    try:
        run = _canonical_run(session)
        if run is None:
            return pd.DataFrame(columns=_LLM_GAPS_COLUMNS)
        q = (
            select(GapSkill, Program, University)
            .join(AlignmentResult, GapSkill.result_id == AlignmentResult.id)
            .join(Program, AlignmentResult.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(AlignmentResult.run_id == run.id, GapSkill.category.isnot(None))
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        records = [{
            "university": uni.name,
            "program_name": program.name,
            "degree_level": program.degree_level,
            "role_groups": program.relevant_roles,
            "missing_skill": gap.skill_name,
            "job_frequency": gap.job_frequency,
            "category": gap.category,
        } for gap, program, uni in rows]
        return pd.DataFrame.from_records(records, columns=_LLM_GAPS_COLUMNS) if records else pd.DataFrame(columns=_LLM_GAPS_COLUMNS)
    finally:
        session.close()


def load_course_skills(university: str | None) -> dict:
    """course_id (str) -> [skill names], matching course_skills_names_only.json shape."""
    session = get_session()
    try:
        q = (
            select(Course.id, CourseSkill.skill_name)
            .join(CourseSkill, CourseSkill.course_id == Course.id)
            .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(ProgramVersion.is_current == True)  # noqa: E712
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        out: dict[str, list[str]] = {}
        for course_id, skill in rows:
            out.setdefault(str(course_id), []).append(skill)
        return out
    finally:
        session.close()


def load_confidence_tiers(university: str | None) -> dict:
    """course_id (str) -> {tier1: [...], tier2: [...], combined: [...]}."""
    session = get_session()
    try:
        q = (
            select(Course.id, CourseSkill.skill_name, CourseSkill.confidence_tier)
            .join(CourseSkill, CourseSkill.course_id == Course.id)
            .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(ProgramVersion.is_current == True)  # noqa: E712
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()
        out: dict[str, dict[str, list[str]]] = {}
        for course_id, skill, tier in rows:
            key = str(course_id)
            entry = out.setdefault(key, {"tier1": [], "tier2": [], "combined": []})
            entry["tier1" if tier == "high" else "tier2"].append(skill)
            entry["combined"].append(skill)
        return out
    finally:
        session.close()


def load_program_evidence(
    university: str, program_name: str, degree_level: str
) -> tuple[list[dict], list[dict]]:
    """Return the current course-level and official outcome-level evidence.

    This deliberately does not feed analytics. It is an audit trail so users
    can see exactly which source text led to every displayed extracted skill.
    """
    session = get_session()
    try:
        course_rows = session.execute(
            select(Course, CourseSkill)
            .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .outerjoin(CourseSkill, CourseSkill.course_id == Course.id)
            .where(
                University.name == university,
                Program.name == program_name,
                Program.degree_level == degree_level,
                ProgramVersion.is_current == True,  # noqa: E712
            )
            .order_by(Course.id, CourseSkill.skill_name)
        ).all()

        courses_by_id: dict[int, dict] = {}
        for course, skill in course_rows:
            record = courses_by_id.setdefault(course.id, {
                "course_name": course.name,
                "course_name_original": course.name_original,
                "credits": course.credits,
                "description": course.description,
                "source_url": course.source_url,
                "source_language": course.source_language,
                "notes": course.notes,
                "skills": [],
            })
            if skill is not None:
                record["skills"].append({
                    "skill_name": skill.skill_name,
                    "confidence_tier": skill.confidence_tier,
                    "extraction_method": skill.extraction_method,
                    "input_type": skill.input_type,
                })

        outcome_rows = session.execute(
            select(ProgramOutcome, ProgramOutcomeSkill)
            .join(ProgramVersion, ProgramOutcome.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .outerjoin(ProgramOutcomeSkill, ProgramOutcomeSkill.outcome_id == ProgramOutcome.id)
            .where(
                University.name == university,
                Program.name == program_name,
                Program.degree_level == degree_level,
                ProgramVersion.is_current == True,  # noqa: E712
            )
            .order_by(ProgramOutcome.outcome_index, ProgramOutcomeSkill.skill_name)
        ).all()

        outcomes_by_id: dict[int, dict] = {}
        for outcome, skill in outcome_rows:
            record = outcomes_by_id.setdefault(outcome.id, {
                "outcome_text": outcome.outcome_text,
                "outcome_text_original": outcome.outcome_text_original,
                "source_url": outcome.source_url,
                "source_language": outcome.source_language,
                "is_official": outcome.is_official,
                "skills": [],
            })
            if skill is not None:
                record["skills"].append({
                    "skill_name": skill.skill_name,
                    "confidence_tier": None,
                    "extraction_method": skill.extraction_method,
                    "input_type": "program_outcome",
                })

        return list(courses_by_id.values()), list(outcomes_by_id.values())
    finally:
        session.close()


def load_job_skills_by_role(university: str | None = None) -> dict:
    """role -> Counter(skill -> job_count). Job market data is national, not
    per-university, so `university` is accepted for API symmetry but ignored."""
    session = get_session()
    try:
        q = (
            select(JobPosting.it_role_group, JobSkill.skill_name)
            .join(JobSkill, JobSkill.posting_id == JobPosting.id)
            .where(JobPosting.is_active == True)  # noqa: E712
        )
        rows = session.execute(q).all()
        role_skills: dict[str, Counter] = {}
        for role, skill in rows:
            if not role:
                continue
            role_skills.setdefault(role, Counter())
            role_skills[role][skill] += 1
        return role_skills
    finally:
        session.close()


def load_role_posting_counts() -> dict:
    """role -> number of active postings. Needed by the core-skill rule
    ('appears in >= 5% of the role's postings'), which is defined against
    posting counts, not skill-mention counts."""
    from sqlalchemy import func

    session = get_session()
    try:
        rows = session.execute(
            select(JobPosting.it_role_group, func.count(JobPosting.id))
            .where(JobPosting.is_active == True)  # noqa: E712
            .group_by(JobPosting.it_role_group)
        ).all()
        return {role: count for role, count in rows if role}
    finally:
        session.close()


def load_skill_info(skill_names: list[str]) -> dict[str, dict]:
    """skill_name -> {description, where_used} for whichever of the given
    names have been generated so far (pipeline/generate_skill_info.py runs
    incrementally, so a brand-new skill may not have a row yet — callers
    should treat a missing key as "not generated yet", not an error)."""
    from .models import SkillInfo

    if not skill_names:
        return {}
    session = get_session()
    try:
        rows = session.execute(
            select(SkillInfo.skill_name, SkillInfo.description, SkillInfo.where_used)
            .where(SkillInfo.skill_name.in_(skill_names))
        ).all()
        return {name: {"description": desc, "where_used": where} for name, desc, where in rows}
    finally:
        session.close()


def job_skills_coverage() -> dict:
    session = get_session()
    try:
        n_total = session.query(JobPosting).filter(JobPosting.is_active == True).count()  # noqa: E712
        n_covered = (
            session.query(JobPosting.id)
            .join(JobSkill, JobSkill.posting_id == JobPosting.id)
            .filter(JobPosting.is_active == True)  # noqa: E712
            .distinct()
            .count()
        )
        return {"n_total": n_total, "n_covered": n_covered, "n_missing": n_total - n_covered}
    finally:
        session.close()


def load_run_metadata() -> dict:
    """Matches the shape of the old data/runs/.../metadata.json.

    job_snapshot's dates are computed live from active JobPosting rows
    (MIN/MAX posting_date), not read off a single stored column — a fixed
    "collected on <date>" was accurate for the frozen March 2026 snapshot
    but silently went stale the moment postings from a later scrape were
    added on top of it (postings now span multiple collection dates, not
    one), so a single date can no longer honestly describe the data."""
    from sqlalchemy import func

    session = get_session()
    try:
        run = _canonical_run(session)
        if run is None:
            return {}
        n_universities = session.query(University).count()
        n_programs = session.query(Program).count()
        n_courses = session.query(Course).count()
        n_sources = session.query(JobSource).count()

        n_active = session.query(JobPosting).filter(JobPosting.is_active == True).count()  # noqa: E712
        min_date, max_date = session.execute(
            select(func.min(JobPosting.posting_date), func.max(JobPosting.posting_date))
            .where(JobPosting.is_active == True)  # noqa: E712
        ).one()
        n_unknown_date = session.query(JobPosting).filter(
            JobPosting.is_active == True, JobPosting.posting_date.is_(None)  # noqa: E712
        ).count()

        return {
            "run_id": run.run_key,
            "is_canonical": True,
            "experiment": run.experiment,
            "created_at": run.created_at.date().isoformat(),
            "curriculum_snapshot": {
                "collected_at": "2026-03-20",
                "n_universities": n_universities,
                "n_programs": n_programs,
                "n_courses": n_courses,
            },
            "job_snapshot": {
                "collected_at": max_date.isoformat() if max_date else None,
                "earliest_at": min_date.isoformat() if min_date else None,
                "n_it_postings": n_active,
                "n_sources": n_sources,
                "n_unknown_date": n_unknown_date,
                "window": "static",
            },
            "esco_version": run.esco_version,
            "notes": run.notes,
        }
    finally:
        session.close()
