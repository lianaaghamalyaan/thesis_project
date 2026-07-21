"""Evidence Explorer — browse the raw records behind every score.

Read-only transparency endpoints: the job side serves postings with their
extracted skills and the per-skill evidence quotes from the promoted
extraction run (job_skill_extraction_* tables); the program side serves
courses with their extracted skills and confidence tiers. This is the
in-product equivalent of querying the warehouse by hand, so reviewers can
audit "where did this skill come from?" without database access.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from server.db import SessionLocal
from server.models import (
    Course,
    CourseSkill,
    JobPosting,
    JobSkillExtractionPosting,
    JobSkillExtractionRun,
    JobSkillExtractionSkill,
    JobSource,
    Program,
    ProgramVersion,
    University,
)

from ..deps import get_current_user

router = APIRouter(tags=["evidence"])

PAGE_MAX = 50


def _db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/evidence/meta")
def evidence_meta(user: dict = Depends(get_current_user), db: Session = Depends(_db)) -> dict:
    """Filter options + provenance of the extraction run being shown."""
    run = (
        db.query(JobSkillExtractionRun)
        .filter(JobSkillExtractionRun.status == "completed")
        .order_by(JobSkillExtractionRun.created_at.desc())
        .first()
    )
    roles = [r[0] for r in db.query(JobPosting.it_role_group).filter(JobPosting.it_role_group.isnot(None)).distinct().order_by(JobPosting.it_role_group)]
    sources = [r[0] for r in db.query(JobSource.name).order_by(JobSource.name)]
    universities = [r[0] for r in db.query(University.name).order_by(University.name)]
    # Programs grouped by university, so the Courses tab can offer a program
    # picker that narrows to the chosen university (current versions only).
    programs_by_university: dict[str, list[str]] = {}
    prog_rows = (
        db.query(University.name, Program.name, Program.degree_level)
        .join(Program, Program.university_id == University.id)
        .join(ProgramVersion, ProgramVersion.program_id == Program.id)
        .filter(ProgramVersion.is_current.is_(True))
        .distinct()
        .order_by(University.name, Program.name, Program.degree_level)
    )
    for uni, prog, degree in prog_rows:
        programs_by_university.setdefault(uni, []).append(f"{prog} ({degree})")
    return {
        "extraction_run": {
            "run_key": run.run_key,
            "model_name": run.model_name,
            "prompt_version": run.prompt_version,
            "status": run.status,
            "completed_at": run.completed_at.isoformat() if run and run.completed_at else None,
        }
        if run
        else None,
        "role_groups": roles,
        "sources": sources,
        "universities": universities,
        "programs_by_university": programs_by_university,
    }


@router.get("/evidence/jobs")
def evidence_jobs(
    q: str = "",
    role: str = "",
    source: str = "",
    offset: int = 0,
    limit: int = 25,
    user: dict = Depends(get_current_user),
    db: Session = Depends(_db),
) -> dict:
    """Postings + their extracted skills with evidence quotes.

    `q` matches title, company, or an extracted skill name.
    """
    limit = min(max(limit, 1), PAGE_MAX)

    run = (
        db.query(JobSkillExtractionRun)
        .filter(JobSkillExtractionRun.status == "completed")
        .order_by(JobSkillExtractionRun.created_at.desc())
        .first()
    )
    if run is None:
        return {"total": 0, "postings": [], "run_key": None}

    base = (
        db.query(JobPosting)
        .join(JobSource, JobPosting.source_id == JobSource.id)
        .filter(JobPosting.is_active.is_(True), JobPosting.is_it_job.is_(True))
    )
    if role:
        base = base.filter(JobPosting.it_role_group == role)
    if source:
        base = base.filter(JobSource.name == source)
    if q:
        like = f"%{q}%"
        skill_match = (
            db.query(JobSkillExtractionPosting.posting_id)
            .join(JobSkillExtractionSkill, JobSkillExtractionSkill.extraction_posting_id == JobSkillExtractionPosting.id)
            .filter(
                JobSkillExtractionPosting.run_id == run.id,
                JobSkillExtractionSkill.normalized_skill_name.ilike(like),
            )
        )
        base = base.filter(
            or_(
                JobPosting.title.ilike(like),
                JobPosting.company_name.ilike(like),
                JobPosting.id.in_(skill_match),
            )
        )

    total = base.with_entities(func.count(JobPosting.id)).scalar() or 0
    postings = base.order_by(JobPosting.posting_date.desc().nullslast(), JobPosting.id).offset(offset).limit(limit).all()

    # Batch-load evidence for this page's postings from the promoted run.
    ids = [p.id for p in postings]
    ev_rows = (
        db.query(JobSkillExtractionPosting, JobSkillExtractionSkill)
        .join(JobSkillExtractionSkill, JobSkillExtractionSkill.extraction_posting_id == JobSkillExtractionPosting.id)
        .filter(JobSkillExtractionPosting.run_id == run.id, JobSkillExtractionPosting.posting_id.in_(ids))
        .all()
    ) if ids else []
    by_posting: dict[int, list[dict]] = {}
    for ep, sk in ev_rows:
        by_posting.setdefault(ep.posting_id, []).append(
            {
                "skill_name": sk.normalized_skill_name,
                "raw_skill_name": sk.raw_skill_name,
                "evidence_text": sk.evidence_text,
                "evidence_type": sk.evidence_type,
            }
        )

    source_names = {s.id: (s.name, s.source_type) for s in db.query(JobSource).all()}
    return {
        "total": total,
        "run_key": run.run_key,
        "postings": [
            {
                "posting_id": p.id,
                "job_id": p.job_id,
                "job_title": p.title,
                "company_name": p.company_name,
                "location": p.location,
                "employment_type": p.employment_type,
                "seniority_level": p.seniority_level,
                "posting_date": p.posting_date.isoformat() if p.posting_date else None,
                "deadline": p.deadline.isoformat() if p.deadline else None,
                "it_role_group": p.it_role_group,
                "source_name": source_names.get(p.source_id, ("?", "?"))[0],
                "source_type": source_names.get(p.source_id, ("?", "?"))[1],
                "source_url": p.source_url,
                "skills": sorted(by_posting.get(p.id, []), key=lambda s: s["skill_name"].lower()),
            }
            for p in postings
        ],
    }


@router.get("/evidence/courses")
def evidence_courses(
    q: str = "",
    university: str = "",
    program: str = "",
    offset: int = 0,
    limit: int = 25,
    user: dict = Depends(get_current_user),
    db: Session = Depends(_db),
) -> dict:
    """Courses (current program versions only) + extracted skills and tiers.

    `q` matches course name, program name, or an extracted skill name.
    """
    limit = min(max(limit, 1), PAGE_MAX)

    base = (
        db.query(Course, Program, University)
        .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
        .join(Program, ProgramVersion.program_id == Program.id)
        .join(University, Program.university_id == University.id)
        .filter(ProgramVersion.is_current.is_(True))
    )
    if university:
        base = base.filter(University.name == university)
    if program:
        # Arrives as "Program Name (Degree)" from the meta program list.
        name, _, degree = program.rpartition(" (")
        degree = degree.rstrip(")")
        if name and degree:
            base = base.filter(Program.name == name, Program.degree_level == degree)
        else:
            base = base.filter(Program.name == program)
    if q:
        like = f"%{q}%"
        skill_match = db.query(CourseSkill.course_id).filter(CourseSkill.skill_name.ilike(like))
        base = base.filter(
            or_(Course.name.ilike(like), Program.name.ilike(like), Course.id.in_(skill_match))
        )

    total = base.with_entities(func.count(Course.id)).scalar() or 0
    rows = base.order_by(University.name, Program.name, Course.name).offset(offset).limit(limit).all()

    ids = [c.id for c, _p, _u in rows]
    skills = db.query(CourseSkill).filter(CourseSkill.course_id.in_(ids)).all() if ids else []
    by_course: dict[int, list[dict]] = {}
    for s in skills:
        by_course.setdefault(s.course_id, []).append(
            {
                "skill_name": s.skill_name,
                "confidence_tier": s.confidence_tier,
                "extraction_method": s.extraction_method,
                "input_type": s.input_type,
            }
        )

    return {
        "total": total,
        "courses": [
            {
                "course_id": c.id,
                "course_name": c.name,
                "course_name_original": c.name_original,
                "university": u.name,
                "program": p.name,
                "degree": p.degree_level,
                "credits": c.credits,
                "description": c.description,
                "ai_generated": bool(c.notes and "AI-generated" in c.notes),
                "source_url": c.source_url,
                "skills": sorted(by_course.get(c.id, []), key=lambda s: s["skill_name"].lower()),
            }
            for c, p, u in rows
        ],
    }
