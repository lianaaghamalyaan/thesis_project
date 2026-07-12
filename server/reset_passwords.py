"""One-time script: replace every account's password with a fresh, strong,
unique one. Run after the initial seed (which uses a shared placeholder
password) before the app is shown to anyone outside development.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m server.reset_passwords

Prints the new credentials once — store them somewhere safe (a password
manager), they are not recoverable from the DB afterward.
"""
from __future__ import annotations

import secrets
import string

from .auth import hash_password
from .db import SessionLocal
from .models import User

ALPHABET = string.ascii_letters + string.digits


def generate_password(length: int = 16) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def main() -> None:
    session = SessionLocal()
    try:
        users = session.query(User).order_by(User.email).all()
        results = []
        for user in users:
            new_password = generate_password()
            user.password_hash = hash_password(new_password)
            results.append((user.email, new_password))
        session.commit()

        print(f"Reset {len(results)} passwords:\n")
        for email, pw in results:
            print(f"  {email:45s}  {pw}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
