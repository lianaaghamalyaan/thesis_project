from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user

router = APIRouter(tags=["job-skills"])


@router.get("/job-skills-by-role")
def get_job_skills_by_role(user: dict = Depends(get_current_user)) -> dict[str, dict[str, int]]:
    role_skills = queries.load_job_skills_by_role()
    return {role: dict(counter) for role, counter in role_skills.items()}


@router.get("/skills/info")
def get_skills_info(names: str, user: dict = Depends(get_current_user)) -> dict[str, dict]:
    """Batch lookup for the "what is this skill?" tooltip — `names` is a
    comma-separated list so a page showing 20-100 skills makes one request,
    not one per skill. Names with no generated info yet are simply absent
    from the response (pipeline/generate_skill_info.py runs incrementally)."""
    skill_names = [n.strip() for n in names.split(",") if n.strip()]
    return queries.load_skill_info(skill_names)
