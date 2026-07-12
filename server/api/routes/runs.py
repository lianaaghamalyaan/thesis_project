from __future__ import annotations

from fastapi import APIRouter, Depends

from server import queries

from ..deps import get_current_user
from ..schemas import RunMetadata

router = APIRouter(tags=["runs"])


@router.get("/run-metadata", response_model=RunMetadata)
def get_run_metadata(user: dict = Depends(get_current_user)):
    return queries.load_run_metadata()


@router.get("/job-skills-coverage")
def get_job_skills_coverage(user: dict = Depends(get_current_user)):
    return queries.job_skills_coverage()
