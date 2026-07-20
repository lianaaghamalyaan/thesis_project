"""FastAPI entrypoint. Run locally with:
    ./.venv_dashboard/bin/uvicorn server.api.main:app --reload --port 8000

Reuses server/models.py, server/queries.py, server/auth.py, server/db.py
unmodified — this file (and the rest of server/api/) is the only new layer,
an HTTP boundary in front of logic that already existed.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .routes.admin import router as admin_router
from .routes.curriculum import router as curriculum_router
from .routes.curriculum_editor import router as curriculum_editor_router
from .routes.gaps import router as gaps_router
from .routes.job_fit import router as job_fit_router
from .routes.job_skills import router as job_skills_router
from .routes.pdf import router as pdf_router
from .routes.programs import router as programs_router
from .routes.recommendations import router as recommendations_router
from .routes.runs import router as runs_router
from .routes.universities import router as universities_router

app = FastAPI(title="CurriculumLens API", version="0.1.0")

# CORS_ORIGINS: comma-separated list, e.g. "http://localhost:3000,https://curriculumlens.vercel.app"
_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(universities_router)
app.include_router(programs_router)
app.include_router(gaps_router)
app.include_router(curriculum_router)
app.include_router(curriculum_editor_router)
app.include_router(job_skills_router)
app.include_router(runs_router)
app.include_router(admin_router)
app.include_router(recommendations_router)
app.include_router(job_fit_router)
app.include_router(pdf_router)


@app.get("/health")
def health():
    return {"status": "ok"}
