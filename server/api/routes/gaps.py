from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user, resolve_university
from ..schemas import GapSkillRow, LlmGapSkillRow

router = APIRouter(tags=["gaps"])


@router.get("/gaps", response_model=list[GapSkillRow])
def get_gaps(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_gaps(scoped)
    return df.to_dict("records") if not df.empty else []


@router.get("/gaps/llm", response_model=list[LlmGapSkillRow])
def get_llm_gaps(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_llm_gaps(scoped)
    return df.to_dict("records") if not df.empty else []
