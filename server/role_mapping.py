"""Canonical mapping from programs.relevant_roles (the thesis's original
9-category taxonomy) to job_postings.it_role_group (the scraper's newer,
more granular 13-category classification).

Single source of truth — imported by both the live alignment pipeline
(pipeline/compute_alignment.py, which computes the headline coverage score)
and server/analytics.py (which computes Strengths/Gaps/Recommendations for
the same program). These used to maintain independent copies of this
mapping that had drifted apart: "Software Engineering" included
Frontend / JS in one and not the other, and "IT Support / Admin / ERP"
included General IT in one and not the other — so the headline score and
the Strengths list shown right below it on the same page were computed
against two different job-market slices. Fixed 2026-07-20 by moving the
mapping here and having both call sites use it.
"""
from __future__ import annotations

# Roles that appear verbatim in both taxonomies (e.g. "Security",
# "Data / ML / AI") don't need an entry here — resolve_roles() falls
# through to an exact-name match for those.
ROLE_ALIASES: dict[str, set[str]] = {
    "Software Engineering": {"Backend", "Frontend / JS", "Full Stack", "General IT"},
    "IT Support / Admin / ERP": {"IT Support / Admin", "General IT"},
}


def resolve_roles(role_set: set[str], known_roles: set[str]) -> set[str]:
    """Resolve each program-side role to job-posting role(s): explicit
    alias, then exact match, then prefix match in either direction (so a
    naming drift doesn't silently zero out a program's score)."""
    resolved: set[str] = set()
    for role in role_set:
        if role in ROLE_ALIASES:
            resolved |= ROLE_ALIASES[role]
            continue
        if role in known_roles:
            resolved.add(role)
            continue
        candidates = [k for k in known_roles if k.startswith(role) or role.startswith(k)]
        if len(candidates) == 1:
            resolved.add(candidates[0])
        elif candidates:
            resolved.add(max(candidates, key=len))
        else:
            print(f"  WARNING: program role {role!r} has no match among known job roles "
                  f"{sorted(known_roles)} — it will contribute nothing to that program's score.")
    return resolved


def expand_program_roles(relevant_roles: str | None, known_roles: set[str]) -> set[str]:
    """Parse a programs.relevant_roles string (comma-separated, or the
    literal "ALL" for general programs compared against the whole market)
    into a set of job_postings.it_role_group values."""
    if not relevant_roles or str(relevant_roles) in ("unmapped", "nan", ""):
        return set()
    if relevant_roles == "ALL":
        return set(known_roles)
    return resolve_roles({r.strip() for r in str(relevant_roles).split(",")}, known_roles)
