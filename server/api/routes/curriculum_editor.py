"""'My Curriculum' — lets a university's own org_admin account confirm that
a course teaches a skill the LLM extraction missed (e.g. because the
published course description is thin — the exact documentation-gap problem
the rest of this dashboard already surfaces but can't resolve on its own).

Every route here is gated by require_curriculum_editor (server/api/deps.py:
org_type == "university" AND role == "org_admin" — never a policy/internal
superadmin standing in, never a "viewer"-tier account) AND re-checks course
ownership against the caller's own university on every write via
queries.get_course_university(), so trusting the client is never the only
thing standing between one university and another's data.

These are the first mutation endpoints in this API — everything else is
read-only, with all writes previously confined to pipeline/ scripts run by
a human. Kept deliberately narrow in scope (create/delete one row) rather
than a general-purpose write API.
"""
from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, status

from server import analytics, queries
from server.db import get_session
from server.models import CourseSkillAssertion

from ..deps import require_curriculum_editor
from ..schemas import CoveragePreview, CreateAssertionRequest, EditorProgram

router = APIRouter(tags=["curriculum-editor"])


@router.get("/admin/curriculum-editor", response_model=list[EditorProgram])
def get_curriculum_editor(user: dict = Depends(require_curriculum_editor)):
    return queries.load_curriculum_editor_data(user["university_name"])


@router.post("/admin/assertions", status_code=status.HTTP_201_CREATED)
def create_assertion(body: CreateAssertionRequest, user: dict = Depends(require_curriculum_editor)):
    owner_university = queries.get_course_university(body.course_id)
    if owner_university != user["university_name"]:
        # Deliberately the same 404 whether the course doesn't exist or
        # belongs to another university — a 403 would leak "that course_id
        # exists, just not yours" to a user who has no business knowing it
        # does at all.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")

    skill_name = body.skill_name.strip()
    if not skill_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "skill_name is required")

    session = get_session()
    try:
        existing = session.query(CourseSkillAssertion).filter(
            CourseSkillAssertion.course_id == body.course_id,
            CourseSkillAssertion.skill_name == skill_name,
        ).first()
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Already confirmed for this course")

        assertion = CourseSkillAssertion(
            course_id=body.course_id,
            skill_name=skill_name,
            asserted_by_user_id=user["user_id"],
            evidence_note=body.evidence_note,
        )
        session.add(assertion)
        session.commit()
        return {"id": assertion.id, "skill_name": assertion.skill_name}
    finally:
        session.close()


@router.delete("/admin/assertions/{assertion_id}")
def delete_assertion(assertion_id: int, user: dict = Depends(require_curriculum_editor)):
    session = get_session()
    try:
        assertion = session.get(CourseSkillAssertion, assertion_id)
        if assertion is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
        owner_university = queries.get_course_university(assertion.course_id)
        if owner_university != user["university_name"]:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
        session.delete(assertion)
        session.commit()
        return {"ok": True}
    finally:
        session.close()


def _num(value) -> float | None:
    """pandas cell -> float or None (NaN/missing/non-numeric all become None),
    so a missing stored score falls back to the live recompute cleanly."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _project(stored: float | None, live_current: float | None, live_with: float | None) -> float | None:
    """The "with your confirmations" number, anchored to the stored canonical
    level, not to the live recompute. We trust the pipeline's official value
    for the *level* (so the baseline always equals the headline shown on
    Program Detail) and trust the live engine only for the *increment* the
    confirmations add — the two live numbers share one formula, so their
    difference is a clean marginal effect even if the live baseline has
    drifted from the stored run (different consolidation/window snapshot).
    Falls back to the full live number only when there's no stored value to
    anchor to (e.g. an "ALL"-mapped program with no core score)."""
    if stored is None:
        return live_with
    if live_current is None or live_with is None:
        return stored
    return round(stored + (live_with - live_current), 2)


@router.get("/admin/coverage-preview", response_model=CoveragePreview)
def get_coverage_preview(program: str, degree: str, user: dict = Depends(require_curriculum_editor)):
    """The "if we count your confirmed skills too" preview. The "current"
    side is the stored canonical score (identical to the headline everywhere
    else in the app), and "with_assertions" adds only the live-computed
    increment from the confirmations on top of it — see _project() and
    CoveragePreview's docstring for why the baseline is anchored, not
    re-derived. Neither is written back; the official score still only moves
    on the next pipeline.compute_alignment.py run."""
    university = user["university_name"]

    alignment_df = queries.load_alignment(university)
    row = alignment_df[(alignment_df["program"] == program) & (alignment_df["degree"] == degree)]
    if row.empty:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Program not found")
    record = row.iloc[0]
    relevant_roles = record.get("relevant_roles")

    stored_core_n = _num(record.get("core_n_job_skills"))
    stored_overlap = _num(record.get("core_n_overlap"))
    stored_core_pct = _num(record.get("core_role_coverage_pct"))
    stored_weighted = _num(record.get("weighted_core_coverage_pct"))

    curriculum_df = queries.load_curriculum(university)
    course_skills = queries.load_course_skills(university)
    job_skills_by_role = queries.load_job_skills_by_role()
    role_posting_counts = queries.load_role_posting_counts()

    extracted_skills = analytics.get_program_skills(program, degree, curriculum_df, course_skills)

    editor_data = queries.load_curriculum_editor_data(university)
    asserted_skills: set[str] = set()
    for prog_entry in editor_data:
        if prog_entry["program"] != program or prog_entry["degree"] != degree:
            continue
        for course in prog_entry["courses"]:
            asserted_skills.update(a["skill_name"] for a in course["assertions"])

    live_current = analytics.compute_role_aware_coverage(
        extracted_skills, relevant_roles, job_skills_by_role, role_posting_counts
    )
    live_with = analytics.compute_role_aware_coverage(
        extracted_skills | asserted_skills, relevant_roles, job_skills_by_role, role_posting_counts
    )

    # Baseline: stored canonical where available (matches the headline), live otherwise.
    core_n_job_skills = int(stored_core_n) if stored_core_n is not None else live_current["core_n_job_skills"]
    current_overlap = int(stored_overlap) if stored_overlap is not None else live_current["core_n_overlap"]
    current_core_pct = stored_core_pct if stored_core_pct is not None else live_current["core_role_coverage_pct"]
    current_weighted = stored_weighted if stored_weighted is not None else live_current["weighted_core_coverage_pct"]

    projected_overlap = _project(
        float(current_overlap) if current_overlap is not None else None,
        live_current["core_n_overlap"], live_with["core_n_overlap"],
    )

    return {
        "core_n_job_skills": core_n_job_skills,
        "current_core_n_overlap": current_overlap,
        "current_core_role_coverage_pct": current_core_pct,
        "current_weighted_core_coverage_pct": current_weighted,
        "with_assertions_core_n_overlap": int(round(projected_overlap)) if projected_overlap is not None else None,
        "with_assertions_core_role_coverage_pct": _project(
            current_core_pct, live_current["core_role_coverage_pct"], live_with["core_role_coverage_pct"]
        ),
        "with_assertions_weighted_core_coverage_pct": _project(
            current_weighted, live_current["weighted_core_coverage_pct"], live_with["weighted_core_coverage_pct"]
        ),
    }
