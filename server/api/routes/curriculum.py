from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user, resolve_university
from ..schemas import CurriculumCourse

router = APIRouter(tags=["curriculum"])


@router.get("/curriculum", response_model=list[CurriculumCourse])
def get_curriculum(university: str | None = None, user: dict = Depends(get_current_user)):
    scoped = resolve_university(university, user)
    df = queries.load_curriculum(scoped)
    return df.to_dict("records") if not df.empty else []
