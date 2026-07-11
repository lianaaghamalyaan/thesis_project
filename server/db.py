"""Database engine and session factory.

Connection resolution order:
1. DATABASE_URL environment variable (production / Docker)
2. .env file in the repo root (local development, gitignored)
3. Local Homebrew Postgres default (current dev machine)

The same code runs against local Postgres (browse it in pgAdmin) and the
deployed server's Postgres — only DATABASE_URL changes.
"""
from __future__ import annotations

import getpass
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql+psycopg2://{getpass.getuser()}@localhost:5432/curriculumlens",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session():
    return SessionLocal()
