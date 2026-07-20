"""PDF program brief export. Reuses dashboard/src/report.py::build_program_pdf
as-is — that module is already Streamlit-free (pure fpdf2 + formatting
helpers), so no porting needed, just a sys.path addition to reach it."""
from __future__ import annotations

import sys
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[3] / "dashboard"
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))

from fastapi import APIRouter, Depends, HTTPException, Response, status  # noqa: E402
from src.report import build_program_pdf  # noqa: E402

from server import analytics, queries  # noqa: E402

from ..deps import get_current_user, resolve_university  # noqa: E402

router = APIRouter(tags=["pdf"])


@router.get("/programs/{program}/{degree}/brief.pdf")
def program_brief_pdf(
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
    record = row.iloc[0]
    relevant_roles = record.get("relevant_roles")
    score = record.get("core_role_coverage_pct")
    score = None if score is None or (isinstance(score, float) and score != score) else float(score)

    curriculum_df = queries.load_curriculum(scoped)
    course_skills = queries.load_course_skills(scoped)
    tiers = queries.load_confidence_tiers(scoped)
    job_skills_by_role = queries.load_job_skills_by_role()
    role_posting_counts = queries.load_role_posting_counts()

    strengths = analytics.get_strengths(
        program, degree, relevant_roles, curriculum_df, course_skills, job_skills_by_role, role_posting_counts, n=20
    ) if relevant_roles not in (None, "unmapped", "nan", "") else []

    doc_score = analytics.compute_program_doc_score(program, degree, curriculum_df, tiers)
    gap_type = analytics.classify_gap_type(doc_score)
    gap_type_labels = {
        "curriculum_gap": "Likely curriculum gap",
        "documentation_gap": "Possible documentation gap",
        "uncertain": "Unclear",
    }

    llm_gaps_df = queries.load_llm_gaps(scoped)
    prog_llm_gaps = llm_gaps_df[
        (llm_gaps_df["program_name"] == program) & (llm_gaps_df["degree_level"] == degree)
    ].sort_values("job_frequency", ascending=False) if not llm_gaps_df.empty else llm_gaps_df

    if not prog_llm_gaps.empty:
        gaps_list = [{"skill": r["missing_skill"], "job_frequency": r["job_frequency"]} for _, r in prog_llm_gaps.iterrows()]
    else:
        fallback_gaps_df = queries.load_gaps(scoped)
        prog_gaps = fallback_gaps_df[
            (fallback_gaps_df["program"] == program) & (fallback_gaps_df["degree"] == degree)
        ].sort_values("job_frequency", ascending=False) if not fallback_gaps_df.empty else fallback_gaps_df
        gaps_list = [{"skill": r["gap_skill"], "job_frequency": r["job_frequency"]} for _, r in prog_gaps.iterrows()]

    all_alignment_df = queries.load_alignment(university=None)
    benchmark = analytics.peer_benchmark(all_alignment_df, scoped, degree, relevant_roles) if score is not None else None

    meta = queries.load_run_metadata()

    n_covered = record.get("core_n_overlap")
    n_total = record.get("core_n_job_skills")
    n_gap = len(gaps_list)

    pdf_bytes = build_program_pdf(
        university=scoped,
        program=program,
        degree=degree,
        score=score,
        relevant_roles=relevant_roles,
        n_covered=int(n_covered) if n_covered is not None else 0,
        n_gap=n_gap,
        n_total=int(n_total) if n_total is not None else 0,
        doc_score=doc_score,
        gap_type_label=gap_type_labels[gap_type],
        strengths=strengths,
        gaps=gaps_list,
        snapshot_date=meta.get("job_snapshot", {}).get("collected_at", "—"),
        benchmark=benchmark,
    )

    filename = f"{program.replace(' ', '_')}_{degree}_brief.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
