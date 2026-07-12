from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user

router = APIRouter(tags=["universities"])


@router.get("/universities")
def list_universities(user: dict = Depends(get_current_user)) -> list[str]:
    return queries.list_universities()
