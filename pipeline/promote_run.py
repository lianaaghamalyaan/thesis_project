"""Promote an AlignmentRun to canonical (what the dashboard shows) — or list
runs to pick one. Demotes whichever run was canonical before, without
deleting it; full history stays queryable.

Usage:
    ./.venv_dashboard/bin/python -m pipeline.promote_run --list
    ./.venv_dashboard/bin/python -m pipeline.promote_run --run-key live_20260712_030000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.db import get_session  # noqa: E402
from server.models import AlignmentRun  # noqa: E402


def list_runs() -> None:
    session = get_session()
    try:
        runs = session.query(AlignmentRun).order_by(AlignmentRun.created_at.desc()).all()
        for run in runs:
            marker = "  <- CANONICAL (live on the dashboard)" if run.is_canonical else ""
            print(f"{run.run_key:30s} {run.created_at}  {run.experiment:25s} "
                  f"postings={run.n_active_postings}{marker}")
    finally:
        session.close()


def promote(run_key: str) -> None:
    session = get_session()
    try:
        target = session.query(AlignmentRun).filter(AlignmentRun.run_key == run_key).first()
        if target is None:
            print(f"No run found with run_key={run_key!r}. Use --list to see available runs.", file=sys.stderr)
            sys.exit(1)
        session.query(AlignmentRun).filter(AlignmentRun.is_canonical == True).update({"is_canonical": False})  # noqa: E712
        target.is_canonical = True
        session.commit()
        print(f"Promoted '{run_key}' to canonical. This is now what every dashboard page shows.")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--run-key", default=None)
    args = parser.parse_args()

    if args.list or not args.run_key:
        list_runs()
        return
    promote(args.run_key)


if __name__ == "__main__":
    main()
