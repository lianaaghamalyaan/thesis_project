from __future__ import annotations

import math

from fastapi import APIRouter, Depends

from server import analytics, queries

from ..deps import get_current_user, require_admin, resolve_university
from ..schemas import ProgramAlignment

router = APIRouter(tags=["admin"])


def _clean_nan(records: list[dict]) -> list[dict]:
    """DataFrame.to_dict("records") leaves NaN for missing values (numeric
    AND string columns, e.g. relevant_roles); JSON/pydantic has no NaN
    literal, so normalize to None before the response model validates it."""
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None
    return records


@router.get("/all-universities", response_model=list[ProgramAlignment])
def get_all_universities(user: dict = Depends(require_admin)):
    """Cross-university alignment data — policy/internal accounts only.
    Mirrors dashboard/pages/all_universities.py's gate."""
    df = queries.load_alignment(university=None)
    # Same non-IT-program exclusion as /programs (see that route for why).
    if not df.empty:
        df = df[df["relevant_roles"].notna()]
    return _clean_nan(df.to_dict("records")) if not df.empty else []


@router.get("/admin/doc-quality")
def get_doc_quality(university: str | None = None, user: dict = Depends(get_current_user)):
    """Documentation quality by program + courses with missing/short
    descriptions. Mirrors dashboard/pages/admin.py, which had no extra gate
    beyond normal university scoping — a university account can see its own
    program's documentation quality, same as before."""
    scoped = resolve_university(university, user)
    alignment_df = queries.load_alignment(scoped)
    curriculum_df = queries.load_curriculum(scoped)
    tiers = queries.load_confidence_tiers(scoped)
    # Same non-IT-program exclusion as /programs — these have no role
    # mapping and no score, so a documentation-quality row for them is noise.
    if not alignment_df.empty:
        alignment_df = alignment_df[alignment_df["relevant_roles"].notna()]

    rows = []
    for _, row in alignment_df.sort_values("weighted_core_coverage_pct", ascending=False, na_position="last").iterrows():
        # In "all universities" mode curriculum_df spans every institution, and
        # program name + degree alone isn't unique across universities (e.g.
        # "Informatics (Computer Science)" exists at both NPUA and NUACA) — scope
        # to this row's university first so two programs' courses never get merged.
        program_curriculum_df = curriculum_df[curriculum_df["university"] == row["university"]]
        doc_score = analytics.compute_program_doc_score(row["program"], row["degree"], program_curriculum_df, tiers)
        breakdown = analytics.program_documentation_breakdown(row["program"], row["degree"], program_curriculum_df)
        rows.append({
            "university": row["university"],
            "program": row["program"],
            "degree": row["degree"],
            "n_courses": breakdown["n_courses"],
            "doc_score": doc_score,
            "documentation_level": breakdown["level"],
            "n_missing": breakdown["missing"],
            "n_ai_generated": breakdown["ai_generated"],
            "n_short": breakdown["short"],
            "n_full": breakdown["full"],
        })

    missing_desc = curriculum_df[
        curriculum_df["description"].isna() | (curriculum_df["description"].str.len() < 50)
    ] if not curriculum_df.empty else curriculum_df
    missing = missing_desc[["program_name", "degree_level", "course_name", "description"]].to_dict("records") \
        if not missing_desc.empty else []
    for m in missing:
        if isinstance(m.get("description"), float) and math.isnan(m["description"]):
            m["description"] = None

    return {"programs": rows, "missing_descriptions": missing}
