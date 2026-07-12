from __future__ import annotations

import math

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user, resolve_university
from ..schemas import GapSkillRow, LlmGapSkillRow

router = APIRouter(tags=["gaps"])


def _clean_nan(records: list[dict]) -> list[dict]:
    """pandas turns None into NaN in numeric columns (e.g. a NULL
    job_frequency); JSON/pydantic reject NaN, which 500s the endpoint —
    same failure mode fixed in routes/admin.py."""
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None
    return records


@router.get("/gaps", response_model=list[GapSkillRow])
def get_gaps(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_gaps(scoped)
    return _clean_nan(df.to_dict("records")) if not df.empty else []


@router.get("/gaps/llm", response_model=list[LlmGapSkillRow])
def get_llm_gaps(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_llm_gaps(scoped)
    return _clean_nan(df.to_dict("records")) if not df.empty else []
