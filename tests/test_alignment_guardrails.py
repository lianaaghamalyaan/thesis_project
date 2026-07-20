"""C2 guardrails, added 2026-07-20 before enabling automated weekly recomputes.
Two near-misses this session (a wrong-source-file bug and a skill-vocabulary
regression, both caught only by a human noticing an implausible number) made
clear that automation without tests is not safe. These three checks are the
minimum bar:

1. test_validate_650_stability — the live pipeline still reproduces a known,
   currently-correct baseline on a fixed historical postings set (catches a
   matching-logic regression, independent of any given week's data).
2. test_role_mapping_* — the headline score and Strengths/Gaps can't drift
   back onto two different job-market slices (see server/role_mapping.py's
   docstring for the incident this prevents).
3. test_promotion_gate_* — pipeline/verify_promotion_gate.py's pure decision
   logic behaves correctly on synthetic before/after data, independent of
   whatever real data happens to be in the database when CI runs.
"""
from __future__ import annotations

import contextlib
import io
import re

import pytest

from conftest import requires_db

from pipeline.verify_promotion_gate import (
    check_no_new_nulls,
    check_program_set,
    check_score_movement,
)
from server.role_mapping import ROLE_ALIASES, expand_program_roles, resolve_roles


# ── 1. validate-650 stability snapshot ─────────────────────────────────────

# Current baseline as of 2026-07-20 (see pipeline/compute_alignment.py's
# docstring for why this is NOT the original thesis-published 62.5%/75.46% —
# that reproduction went void when job-skills extraction methodology
# upgraded 2026-07-15; this snapshot is the new, current-methodology
# baseline). Update these two numbers (and this comment's date) only after
# manually confirming a new number is correct, never to make a failing test
# pass without understanding why it moved.
EXPECTED_CORE = 43.04
EXPECTED_WEIGHTED = 55.21
TOLERANCE_PTS = 2.0


@requires_db
def test_validate_650_stability():
    from pipeline.compute_alignment import compute_alignment

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        compute_alignment(university="Yerevan State University", dry_run=True, validate_650=True)
    output = buf.getvalue()

    line = next((l for l in output.splitlines() if "Data Science in Business" in l), None)
    assert line is not None, f"Could not find 'Data Science in Business' in dry-run output:\n{output}"

    core_match = re.search(r"core=\s*([\d.]+)", line)
    weighted_match = re.search(r"weighted=\s*([\d.]+)", line)
    assert core_match and weighted_match, f"Could not parse core/weighted from line: {line!r}"

    core = float(core_match.group(1))
    weighted = float(weighted_match.group(1))

    assert abs(core - EXPECTED_CORE) <= TOLERANCE_PTS, (
        f"--validate-650 core coverage for YSU Data Science in Business moved from "
        f"{EXPECTED_CORE} to {core} (tolerance {TOLERANCE_PTS} pts) — likely a matching-logic "
        f"regression. If this is a deliberate, verified methodology change, update EXPECTED_CORE."
    )
    assert abs(weighted - EXPECTED_WEIGHTED) <= TOLERANCE_PTS, (
        f"--validate-650 weighted coverage for YSU Data Science in Business moved from "
        f"{EXPECTED_WEIGHTED} to {weighted} (tolerance {TOLERANCE_PTS} pts) — likely a matching-logic "
        f"regression. If this is a deliberate, verified methodology change, update EXPECTED_WEIGHTED."
    )


# ── 2. single role-mapping source of truth ─────────────────────────────────

def test_compute_alignment_imports_shared_role_mapping():
    """Regression test for the exact incident server/role_mapping.py's
    docstring describes: pipeline/compute_alignment.py must resolve program
    roles via the shared module, not a locally-redefined copy."""
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[1] / "pipeline" / "compute_alignment.py").read_text()
    assert "from server.role_mapping import expand_program_roles" in src
    assert re.search(r"^ROLE_ALIASES\s*[:=]", src, re.MULTILINE) is None, (
        "pipeline/compute_alignment.py appears to define its own ROLE_ALIASES again — "
        "this is exactly the drift server/role_mapping.py was created to prevent."
    )


def test_analytics_imports_shared_role_mapping():
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[1] / "server" / "analytics.py").read_text()
    assert "from .role_mapping import expand_program_roles" in src
    assert re.search(r"^ROLE_MAPPING\s*[:=]", src, re.MULTILINE) is None, (
        "server/analytics.py appears to define its own ROLE_MAPPING again — "
        "this is exactly the drift server/role_mapping.py was created to prevent."
    )


def test_role_alias_resolution_behavior():
    known_roles = {"Backend", "Frontend / JS", "Full Stack", "General IT", "IT Support / Admin",
                    "Data / ML / AI", "Security"}
    assert resolve_roles({"Software Engineering"}, known_roles) == ROLE_ALIASES["Software Engineering"]
    # A program mapped only to a role with no alias (exact match already in known_roles).
    assert resolve_roles({"Security"}, known_roles) == {"Security"}


def test_expand_program_roles_handles_all():
    known_roles = {"Backend", "Data / ML / AI", "Security"}
    assert expand_program_roles("ALL", known_roles) == known_roles
    assert expand_program_roles(None, known_roles) == set()
    assert expand_program_roles("unmapped", known_roles) == set()


# ── 3. promotion gate pure-logic unit tests ────────────────────────────────

def test_check_program_set_flags_missing_program():
    problems = check_program_set(old_programs={1, 2, 3}, new_programs={1, 2})
    assert len(problems) == 1
    assert "3" in problems[0]


def test_check_program_set_passes_when_unchanged():
    assert check_program_set(old_programs={1, 2, 3}, new_programs={1, 2, 3}) == []


def test_check_no_new_nulls_flags_independent_null():
    old_scores = {1: (20.0, 25.0)}
    new_scores = {1: (None, 25.0)}  # core went null, weighted didn't — always a bug
    problems = check_no_new_nulls(old_scores, new_scores)
    assert len(problems) == 1


def test_check_no_new_nulls_allows_both_going_null_together():
    old_scores = {1: (20.0, 25.0)}
    new_scores = {1: (None, None)}  # legitimate: role now has zero postings
    assert check_no_new_nulls(old_scores, new_scores) == []


def test_check_score_movement_passes_on_few_outliers():
    old = {i: 20.0 for i in range(40)}
    new = dict(old)
    new[0] = 35.0  # one program moved +15 pts — 1/40 = 2.5%, well under 15% fail threshold
    problems, moved = check_score_movement(old, new)
    assert problems == []
    assert len(moved) == 1


def test_check_score_movement_fails_on_systemic_shift():
    old = {i: 20.0 for i in range(40)}
    new = {i: 40.0 for i in range(40)}  # every program jumped 20 pts — looks like a bug, not real drift
    problems, moved = check_score_movement(old, new)
    assert len(problems) == 1
    assert len(moved) == 40


def test_check_score_movement_ignores_small_moves():
    old = {i: 20.0 for i in range(10)}
    new = {i: 22.0 for i in range(10)}  # +2 pts each — under the 10-pt flag threshold
    problems, moved = check_score_movement(old, new)
    assert problems == []
    assert moved == []
