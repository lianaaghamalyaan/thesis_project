from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user

router = APIRouter(tags=["job-skills"])


@router.get("/job-skills-by-role")
def get_job_skills_by_role(user: dict = Depends(get_current_user)) -> dict[str, dict[str, int]]:
    role_skills = queries.load_job_skills_by_role()
    return {role: dict(counter) for role, counter in role_skills.items()}
