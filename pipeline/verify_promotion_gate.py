"""General-purpose promotion gate: decides whether a freshly-computed
AlignmentRun is safe to promote to canonical, without a human eyeballing a
before/after table first. Exit code 0 = safe to promote, 1 = do not.

This generalizes the one-off pipeline/verify_full_refresh.py (written for
one specific curriculum+job-skills refresh, with hardcoded expected values
for that event) into something automation can call after every routine
recompute — the C2 guardrail this repo didn't have before 2026-07-20,
despite two near-misses this session (a wrong-source-file bug and a
skill-vocabulary regression, both caught only by a human noticing an
implausible number).

Checks, in order (first failure stops and reports):
  1. Same set of programs scored in both runs — catches a program silently
     dropped (e.g. a role-mapping bug that zeroes out a program's role_set).
  2. No program that had a score in the old run comes back NULL in the new
     one, unless BOTH core_role_coverage_pct AND weighted_core_coverage_pct
     went NULL together (a legitimate "this role now has zero postings"
     case, not a bug) — one going NULL and not the other is never legitimate
     and always a bug.
  3. Score movement is bounded: flags any program whose weighted headline
     score moved by more than MOVEMENT_FLAG_PTS points, and hard-fails if
     more than MOVEMENT_FAIL_FRACTION of scored programs moved by more than
     that — a few programs moving a lot from a real data change is normal
     (see e.g. the July 2026 refresh); most programs moving a lot at once is
     the signature of a systemic bug (a broken join, a corrupted vocabulary,
     a role-mapping regression), not real-world drift.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.verify_promotion_gate --run-key live_20260720_120000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MOVEMENT_FLAG_PTS = 10.0
MOVEMENT_FAIL_FRACTION = 0.15


def check_program_set(old_programs: set[int], new_programs: set[int]) -> list[str]:
    """Pure function, no DB — testable in isolation."""
    problems = []
    missing = old_programs - new_programs
    if missing:
        problems.append(f"{len(missing)} program(s) present in the old run are missing from the new one: "
                         f"{sorted(missing)[:10]}{'...' if len(missing) > 10 else ''}")
    return problems


def check_no_new_nulls(
    old_scores: dict[int, tuple[float | None, float | None]],
    new_scores: dict[int, tuple[float | None, float | None]],
) -> list[str]:
    """old_scores/new_scores: program_id -> (core_role_coverage_pct, weighted_core_coverage_pct).
    Pure function, no DB — testable in isolation."""
    problems = []
    for pid, (old_core, old_weighted) in old_scores.items():
        if pid not in new_scores:
            continue  # already reported by check_program_set
        new_core, new_weighted = new_scores[pid]
        core_went_null = old_core is not None and new_core is None
        weighted_went_null = old_weighted is not None and new_weighted is None
        if core_went_null != weighted_went_null:
            problems.append(
                f"program {pid}: core/weighted went NULL independently of each other "
                f"(core {old_core}->{new_core}, weighted {old_weighted}->{new_weighted}) — "
                "these should always change together."
            )
    return problems


def check_score_movement(
    old_weighted: dict[int, float], new_weighted: dict[int, float],
    flag_pts: float = MOVEMENT_FLAG_PTS, fail_fraction: float = MOVEMENT_FAIL_FRACTION,
) -> tuple[list[str], list[tuple[int, float, float]]]:
    """old_weighted/new_weighted: program_id -> weighted_core_coverage_pct, only for
    programs present with a non-null score in BOTH runs. Returns (hard failures,
    flagged movements) — flagged movements alone are informational, not a failure,
    unless too many of them happen at once. Pure function, no DB — testable in
    isolation."""
    common = sorted(set(old_weighted) & set(new_weighted))
    moved = [(pid, old_weighted[pid], new_weighted[pid]) for pid in common
             if abs(new_weighted[pid] - old_weighted[pid]) > flag_pts]

    problems = []
    if common and len(moved) / len(common) > fail_fraction:
        problems.append(
            f"{len(moved)} of {len(common)} scored programs ({len(moved)/len(common)*100:.0f}%) moved by more "
            f"than {flag_pts} points — that's more than the {fail_fraction*100:.0f}% expected from real-world "
            "data drift and looks like a systemic bug (broken join, corrupted vocabulary, role-mapping "
            "regression) rather than legitimate movement."
        )
    return problems, moved


def run_gate(old_run_key: str | None, new_run_key: str) -> bool:
    """Returns True if safe to promote. Prints a full report either way."""
    from sqlalchemy import text

    from server.db import get_session

    session = get_session()
    try:
        if old_run_key is None:
            row = session.execute(text("SELECT run_key FROM alignment_runs WHERE is_canonical = true")).one_or_none()
            if row is None:
                print("No canonical run exists yet — nothing to compare against. Treating as safe (first run).")
                return True
            old_run_key = row[0]

        def load(run_key: str) -> dict[int, tuple[float | None, float | None]]:
            rows = session.execute(text("""
                SELECT ar.program_id, ar.core_role_coverage_pct, ar.weighted_core_coverage_pct
                FROM alignment_results ar
                JOIN alignment_runs r ON r.id = ar.run_id
                WHERE r.run_key = :k
            """), {"k": run_key}).all()
            return {pid: (core, weighted) for pid, core, weighted in rows}

        old_scores = load(old_run_key)
        new_scores = load(new_run_key)
        if not old_scores:
            print(f"WARNING: old run {old_run_key!r} has no alignment_results rows — skipping comparison.")
            return True
        if not new_scores:
            print(f"FAIL: new run {new_run_key!r} has no alignment_results rows at all.")
            return False

        all_problems: list[str] = []
        all_problems += check_program_set(set(old_scores), set(new_scores))
        all_problems += check_no_new_nulls(old_scores, new_scores)

        old_weighted = {pid: w for pid, (_c, w) in old_scores.items() if w is not None}
        new_weighted = {pid: w for pid, (_c, w) in new_scores.items() if w is not None}
        movement_problems, moved = check_score_movement(old_weighted, new_weighted)
        all_problems += movement_problems

        print(f"Comparing {old_run_key!r} (old, canonical) -> {new_run_key!r} (new).")
        print(f"{len(old_scores)} programs in old run, {len(new_scores)} in new run.")
        if moved:
            print(f"\n{len(moved)} program(s) moved by more than {MOVEMENT_FLAG_PTS} points:")
            for pid, old_w, new_w in sorted(moved, key=lambda x: -abs(x[2] - x[1])):
                print(f"  program_id={pid}: {old_w:.2f} -> {new_w:.2f} ({new_w - old_w:+.2f})")

        if all_problems:
            print("\nFAIL — do not promote:")
            for p in all_problems:
                print(f"  - {p}")
            return False

        print("\nPASS — safe to promote.")
        return True
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-key", required=True, help="The new (non-canonical) run to evaluate.")
    parser.add_argument("--against", default=None, help="Run to compare against (default: current canonical).")
    args = parser.parse_args()

    ok = run_gate(args.against, args.run_key)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
