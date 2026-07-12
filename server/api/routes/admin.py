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

    rows = []
    for _, row in alignment_df.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows():
        doc_score = analytics.compute_program_doc_score(row["program"], row["degree"], curriculum_df, tiers)
        n_courses = len(curriculum_df[
            (curriculum_df["program_name"] == row["program"]) & (curriculum_df["degree_level"] == row["degree"])
        ])
        rows.append({
            "program": row["program"],
            "degree": row["degree"],
            "n_courses": n_courses,
            "doc_score": doc_score,
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
