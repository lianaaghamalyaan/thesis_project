"""POST /auth/login, POST /auth/logout, GET /auth/me.

Credential checking reuses server.auth.authenticate() as-is. What's new here
is turning that into an httpOnly session cookie (JWT) — the old app had no
real session mechanism, just Streamlit's in-process st.session_state.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from server.auth import authenticate
from server.db import get_session
from server.models import University

from .deps import COOKIE_NAME, get_current_user
from .tokens import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Secure+SameSite=None cookies require HTTPS (browsers reject them over
# plain http://localhost during local dev). ENV=production (set on the
# deployed host) switches to the cross-site-safe cookie settings needed
# once frontend and backend live on different domains.
_IS_PROD = os.environ.get("ENV", "development") == "production"


class LoginRequest(BaseModel):
    email: str
    password: str


def _resolve_university_name(university_id: int | None) -> str | None:
    if university_id is None:
        return None
    session = get_session()
    try:
        uni = session.get(University, university_id)
        return uni.name if uni else None
    finally:
        session.close()


@router.post("/login")
def login(body: LoginRequest, response: Response):
    user = authenticate(body.email, body.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")

    if user["org_type"] == "university":
        user["university_name"] = _resolve_university_name(user["university_id"])
    else:
        user["university_name"] = None

    token = create_token(user)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=_IS_PROD,
        samesite="none" if _IS_PROD else "lax",
        max_age=7 * 24 * 3600,
        path="/",
    )
    return {"user": user}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"user": user}
