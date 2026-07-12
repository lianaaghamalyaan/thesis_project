from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from server import analytics, queries

from ..deps import get_current_user, resolve_university

router = APIRouter(tags=["job-fit"])


@router.get("/job-fit")
def get_job_fit(
    program: str,
    degree: str,
    role: str,
    university: str | None = None,
    user: dict = Depends(get_current_user),
):
    scoped = resolve_university(university, user)
    if not scoped:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A university must be specified")

    curriculum_df = queries.load_curriculum(scoped)
    course_skills = queries.load_course_skills(scoped)
    job_skills_by_role = queries.load_job_skills_by_role()

    return analytics.compute_job_fit(program, degree, role, curriculum_df, course_skills, job_skills_by_role)


@router.get("/job-fit/roles")
def list_roles(user: dict = Depends(get_current_user)) -> list[str]:
    return sorted(queries.load_job_skills_by_role().keys())
