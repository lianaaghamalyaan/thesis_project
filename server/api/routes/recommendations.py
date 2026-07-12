from __future__ import annotations

import math

from fastapi import APIRouter, Depends

from server import analytics, queries

from ..deps import get_current_user, resolve_university

router = APIRouter(tags=["recommendations"])


def _clean(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


@router.get("/recommendations")
def get_recommendations(university: str | None = None, user: dict = Depends(get_current_user)):
    """Priority matrix + per-program recommendations + cross-program gap
    priorities. Mirrors dashboard/pages/recommendations.py."""
    scoped = resolve_university(university, user)
    alignment_df = queries.load_alignment(scoped)
    gaps_df = queries.load_gaps(scoped)
    curriculum_df = queries.load_curriculum(scoped)
    tiers = queries.load_confidence_tiers(scoped)

    programs = []
    for _, row in alignment_df.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows():
        score = _clean(row.get("core_role_coverage_pct"))
        doc_score = analytics.compute_program_doc_score(row["program"], row["degree"], curriculum_df, tiers)
        gap_type = analytics.classify_gap_type(doc_score)
        recs = analytics.get_program_recommendations(
            row["program"], row["degree"], score, gaps_df, curriculum_df, tiers
        )
        programs.append({
            "program": row["program"],
            "degree": row["degree"],
            "core_role_coverage_pct": score,
            "doc_score": doc_score,
            "gap_type": gap_type,
            "recommendations": recs,
        })

    cross_gaps_df = analytics.get_cross_program_gaps(gaps_df)
    cross_gaps = cross_gaps_df.to_dict("records") if not cross_gaps_df.empty else []

    return {"programs": programs, "cross_program_gaps": cross_gaps}
