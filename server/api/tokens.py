"""JWT issuing/decoding for the session cookie.

JWT_SECRET resolution mirrors server/db.py's DATABASE_URL pattern: env var,
then .env file, then a local-dev fallback (never used in production — always
set JWT_SECRET explicitly there, e.g. via the hosting platform's env vars).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

from server.db import _load_dotenv

_load_dotenv()

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-insecure-secret-do-not-use-in-prod")
JWT_ALGORITHM = "HS256"
TOKEN_TTL = timedelta(days=7)


def create_token(user: dict) -> str:
    payload = {**user, "exp": datetime.now(timezone.utc) + TOKEN_TTL}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    payload.pop("exp", None)
    return payload
