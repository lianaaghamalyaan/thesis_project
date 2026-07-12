"""FastAPI dependencies: DB session, current-user (from JWT cookie), admin gate.

Mirrors the authorization rules that used to live in dashboard/src/auth_ui.py
(Streamlit session state) — now enforced server-side on every request instead
of just hidden in the UI, since there's a real network boundary now.
"""
from __future__ import annotations

from typing import Generator

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.db import get_session

from .tokens import decode_token

COOKIE_NAME = "cl_session"


def get_db() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


def get_current_user(cl_session: str | None = Cookie(default=None)) -> dict:
    if cl_session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user = decode_token(cl_session)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("org_type") not in ("policy", "internal"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


def resolve_university(requested: str | None, user: dict) -> str | None:
    """Server-side scoping enforcement: a university-tier account can only
    ever see its own university's data, regardless of what the client sends
    — mirrors current_university()'s old implicit session behavior, but now
    as a real authorization check rather than just hidden UI state.
    `university_name` is resolved once at login time (see api/auth.py) and
    baked into the JWT — org.name itself is NOT the plain university name
    (it's "<University> (University Account)", see server/seed.py)."""
    if user.get("org_type") == "university":
        return user.get("university_name")
    return requested
