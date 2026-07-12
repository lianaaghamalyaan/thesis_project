from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, status

from server import analytics, queries

from ..deps import get_current_user, resolve_university
from ..schemas import ProgramAlignment, ProgramDetail

router = APIRouter(tags=["programs"])


def _clean_nan(records: list[dict]) -> list[dict]:
    """DataFrame.to_dict("records") leaves NaN for missing numerics; JSON
    has no NaN literal, so normalize to None before the response model
    validates it."""
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None
    return records


@router.get("/programs", response_model=list[ProgramAlignment])
def list_programs(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_alignment(scoped)
    return _clean_nan(df.to_dict("records")) if not df.empty else []


@router.get("/programs/{program}/{degree}", response_model=ProgramDetail)
def get_program_detail(
    program: str,
    degree: str,
    university: str | None = None,
    user: dict = Depends(get_current_user),
):
    scoped = resolve_university(university, user)
    if not scoped:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A university must be specified")

    alignment_df = queries.load_alignment(scoped)
    row = alignment_df[(alignment_df["program"] == program) & (alignment_df["degree"] == degree)]
    if row.empty:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Program not found")
    alignment_record = _clean_nan(row.to_dict("records"))[0]
    relevant_roles = alignment_record.get("relevant_roles")

    llm_gaps_df = queries.load_llm_gaps(scoped)
    prog_llm_gaps = llm_gaps_df[
        (llm_gaps_df["program_name"] == program) & (llm_gaps_df["degree_level"] == degree)
    ].sort_values("job_frequency", ascending=False) if not llm_gaps_df.empty else llm_gaps_df

    fallback_gaps_df = queries.load_gaps(scoped)
    prog_fallback_gaps = fallback_gaps_df[
        (fallback_gaps_df["program"] == program) & (fallback_gaps_df["degree"] == degree)
    ].sort_values("job_frequency", ascending=False) if not fallback_gaps_df.empty else fallback_gaps_df

    curriculum_df = queries.load_curriculum(scoped)
    course_skills = queries.load_course_skills(scoped)
    tiers = queries.load_confidence_tiers(scoped)
    job_skills_by_role = queries.load_job_skills_by_role()

    strengths = analytics.get_strengths(
        program, degree, relevant_roles, curriculum_df, course_skills, job_skills_by_role, n=20
    ) if relevant_roles not in (None, "unmapped", "nan", "") else []

    doc_score = analytics.compute_program_doc_score(program, degree, curriculum_df, tiers)
    gap_type = analytics.classify_gap_type(doc_score)

    all_alignment_df = queries.load_alignment(university=None)
    score = alignment_record.get("core_role_coverage_pct")
    benchmark = analytics.peer_benchmark(all_alignment_df, scoped, degree, relevant_roles) if score is not None else None

    return {
        "alignment": alignment_record,
        "gaps": _clean_nan(prog_llm_gaps.to_dict("records")) if not prog_llm_gaps.empty else [],
        "fallback_gaps": _clean_nan(prog_fallback_gaps.to_dict("records")) if not prog_fallback_gaps.empty else [],
        "strengths": strengths,
        "benchmark": benchmark,
        "doc_score": doc_score,
        "gap_type": gap_type,
    }
