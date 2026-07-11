"""Password hashing and user authentication.

Uses stdlib PBKDF2-HMAC-SHA256 (no external dependency). Hash format:
    pbkdf2$<iterations>$<salt_hex>$<hash_hex>
"""
from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime

from .db import get_session
from .models import Organization, User

ITERATIONS = 600_000  # OWASP-recommended magnitude for PBKDF2-SHA256


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt_hex, hash_hex = stored.split("$")
        if scheme != "pbkdf2":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), hash_hex)
    except (ValueError, TypeError):
        return False


def authenticate(email: str, password: str) -> dict | None:
    """Check credentials. Returns a session-safe dict (no ORM objects, no hash)
    or None if authentication fails."""
    session = get_session()
    try:
        user = session.query(User).filter(
            User.email == email.strip().lower(), User.is_active == True  # noqa: E712
        ).first()
        if user is None or not verify_password(password, user.password_hash):
            return None
        org = session.get(Organization, user.organization_id)
        user.last_login_at = datetime.utcnow()
        session.commit()
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_id": org.id,
            "org_name": org.name,
            "org_type": org.org_type,           # university | policy | internal
            "university_id": org.university_id,  # set for university orgs
        }
    finally:
        session.close()
