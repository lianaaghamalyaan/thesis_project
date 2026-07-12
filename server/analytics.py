"""Pure business logic shared by the Streamlit dashboard's src/ modules and
the FastAPI backend — ported here (Streamlit-free) so both can call it
without the API process needing a Streamlit dependency.

Mirrors, verbatim in logic, dashboard/src/alignment.py, benchmark.py,
doc_gap.py, recs.py, job_fit_engine.py. Kept side-effect-free (no st.* calls)
— the Streamlit pages' own src/ modules remain the source of truth for
*rendering*, but the actual computation lives here for the API to share.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

MIN_ROLE_MATCHED_PEERS = 3

ROLE_MAPPING = {
    "Software Engineering": ["Backend", "Full Stack", "General IT"],
    "Data / ML / AI": ["Data / ML / AI"],
    "DevOps / Cloud": ["DevOps / Cloud"],
    "Hardware / Embedded": ["Hardware / Embedded"],
    "Security": ["Security"],
    "QA / Testing": ["QA / Testing"],
    "IT Support / Admin / ERP": ["IT Support / Admin", "General IT"],
    "Technical Management": ["Technical Management"],
    "UX / Product Design": ["UX / Product Design"],
}


def expand_roles(relevant_roles: str | None) -> list[str]:
    if not relevant_roles or str(relevant_roles) in ("unmapped", "nan", ""):
        return []
    job_roles = []
    for r in str(relevant_roles).split(","):
        r = r.strip()
        job_roles.extend(ROLE_MAPPING.get(r, [r]))
    return list(dict.fromkeys(job_roles))


def get_program_skills(program: str, degree: str, curriculum_df: pd.DataFrame, course_skills: dict) -> set:
    courses = curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]
    skills: set = set()
    for _, row in courses.iterrows():
        course_id = str(int(row["course_id"]))
        skills.update(course_skills.get(course_id, []))
    return skills


def get_skill_courses(
    program: str, degree: str, curriculum_df: pd.DataFrame, course_skills: dict, tiers: dict
) -> dict[str, list[dict]]:
    """For every skill taught anywhere in this program, which course(s) contributed it —
    the traceability behind a Strengths row: "why did this skill count as covered?" """
    courses = curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]
    out: dict[str, list[dict]] = {}
    for _, row in courses.iterrows():
        course_id = str(int(row["course_id"]))
        course_tier1 = set(tiers.get(course_id, {}).get("tier1", []))
        for skill in course_skills.get(course_id, []):
            out.setdefault(skill, []).append({
                "course_name": row["course_name"],
                "high_confidence": skill in course_tier1,
            })
    return out


def get_role_skill_counter(relevant_roles: str | None, job_skills_by_role: dict) -> Counter:
    job_roles = expand_roles(relevant_roles)
    agg: Counter = Counter()
    for role in job_roles:
        agg.update(job_skills_by_role.get(role, {}))
    return agg


def get_strengths(
    program: str,
    degree: str,
    relevant_roles: str | None,
    curriculum_df: pd.DataFrame,
    course_skills: dict,
    job_skills_by_role: dict,
    n: int = 20,
) -> list[dict]:
    prog_skills = get_program_skills(program, degree, curriculum_df, course_skills)
    role_counter = get_role_skill_counter(relevant_roles, job_skills_by_role)
    matched = [
        {"skill": s, "job_count": role_counter[s]}
        for s in prog_skills
        if s in role_counter
    ]
    matched.sort(key=lambda x: -x["job_count"])
    return matched[:n]


def compute_program_doc_score(program: str, degree: str, curriculum_df: pd.DataFrame, tiers: dict) -> float:
    courses = curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]
    total_tier1 = 0
    total_combined = 0
    for _, row in courses.iterrows():
        course_id = str(int(row["course_id"]))
        tier_data = tiers.get(course_id, {})
        total_tier1 += len(tier_data.get("tier1", []))
        total_combined += len(tier_data.get("combined", []))
    if total_combined == 0:
        return 0.0
    return total_tier1 / total_combined


def classify_gap_type(doc_score: float) -> str:
    if doc_score >= 0.45:
        return "curriculum_gap"
    if doc_score <= 0.20:
        return "documentation_gap"
    return "uncertain"


def _roles_overlap(roles_str, target_roles: set) -> bool:
    if not isinstance(roles_str, str) or roles_str in ("unmapped", "nan", ""):
        return False
    roles = {r.strip() for r in roles_str.split(",")}
    return bool(roles & target_roles)


def peer_benchmark(all_alignment: pd.DataFrame, university: str, degree: str, relevant_roles: str | None) -> dict | None:
    """`all_alignment` is the unfiltered (all-universities) alignment
    DataFrame — same "backend sees everything" pattern as
    dashboard/src/benchmark.py's load_all_universities_alignment()."""
    others = all_alignment[
        (all_alignment["university"] != university)
        & (all_alignment["degree"] == degree)
        & (all_alignment["core_role_coverage_pct"].notna())
    ].copy()

    if others.empty:
        return None

    matched_on = "degree level"
    if relevant_roles and relevant_roles not in ("unmapped", "nan", "", "ALL"):
        target_roles = {r.strip() for r in str(relevant_roles).split(",")}
        role_matched = others[others["relevant_roles"].apply(_roles_overlap, target_roles=target_roles)]
        if len(role_matched) >= MIN_ROLE_MATCHED_PEERS:
            others = role_matched
            matched_on = "role group"

    return {
        "peer_mean": float(others["core_role_coverage_pct"].mean()),
        "peer_median": float(others["core_role_coverage_pct"].median()),
        "peer_max": float(others["core_role_coverage_pct"].max()),
        "peer_n": int(len(others)),
        "matched_on": matched_on,
    }


def get_program_recommendations(
    program: str,
    degree: str,
    core_role_coverage_pct: float | None,
    gaps_df: pd.DataFrame,
    curriculum_df: pd.DataFrame,
    tiers: dict,
) -> list[dict]:
    """3-5 actionable recommendations for a program. Each: {type, title,
    description, priority}. Ported from dashboard/src/recs.py."""
    recs = []

    doc_score = compute_program_doc_score(program, degree, curriculum_df, tiers)

    prog_gaps = gaps_df[
        (gaps_df["program"] == program) & (gaps_df["degree"] == degree)
    ].sort_values("job_frequency", ascending=False) if not gaps_df.empty else gaps_df

    if doc_score < 0.35:
        priority = "high" if doc_score < 0.20 else "medium"
        recs.append({
            "type": "documentation",
            "title": "Update course descriptions",
            "description": (
                "Many courses in this program have limited or vague syllabi. "
                "Improving descriptions to explicitly mention skills taught "
                "could raise the measured alignment score without changing the curriculum content itself."
            ),
            "priority": priority,
        })

    if not prog_gaps.empty:
        top5 = prog_gaps.head(5)
        skill_list = ", ".join(f"**{s}**" for s in top5["gap_skill"])
        top = top5.iloc[0]
        recs.append({
            "type": "curriculum",
            "title": "Consider adding high-demand skills",
            "description": (
                f"The most-requested skills not currently covered: {skill_list}. "
                f"**{top['gap_skill']}** appears in {int(top['job_frequency'])} job postings "
                f"for the relevant role group."
            ),
            "priority": "high",
        })

    if core_role_coverage_pct is not None and not pd.isna(core_role_coverage_pct) and core_role_coverage_pct < 25:
        recs.append({
            "type": "strategy",
            "title": "Bridge theory to applied tooling",
            "description": (
                "Programs with strong theoretical foundations often show lower market alignment "
                "scores because job postings emphasize applied tools and industry frameworks. "
                "Consider adding practical labs, electives, or project work covering "
                "the industry-standard tools for this program's target roles."
            ),
            "priority": "medium",
        })

    recs.append({
        "type": "note",
        "title": "These are data-driven suggestions, not prescriptions",
        "description": (
            "Recommendations are based on automated analysis of Armenian IT job postings "
            "and course descriptions. They are decision-support, not authoritative guidance. "
            "Use them alongside faculty judgment and program goals."
        ),
        "priority": "info",
    })

    return recs


def get_cross_program_gaps(gaps_df: pd.DataFrame) -> pd.DataFrame:
    """Top gap skills appearing across the most programs — university-wide
    priorities. Ported from dashboard/src/recs.py."""
    if gaps_df.empty:
        return pd.DataFrame()
    agg = (
        gaps_df.groupby("gap_skill")
        .agg(n_programs=("program", "nunique"), total_frequency=("job_frequency", "sum"))
        .reset_index()
        .sort_values(["n_programs", "total_frequency"], ascending=[False, False])
    )
    return agg.head(25)


# ── Job Fit (semantic, consistent with the validated pipeline) ────────────
#
# The original Job Fit metric divided exact-string matches by ALL distinct
# skills ever mentioned in a role's postings — for QA / Testing that meant a
# 199-skill denominator of which 131 appear in exactly ONE posting, giving
# absurdly low scores (7.0% for pairs that the headline metric scores far
# higher). Rewritten 2026-07-12 to use the exact same methodology as the
# validated pipeline (pipeline/compute_alignment.py): core-skill filter
# (>= 5% of the role's postings), semantic matching at cosine >= 0.65 with
# the same blocklist/allowlist, frequency-weighted secondary score. With
# identical inputs this reproduces the headline core/weighted numbers
# exactly for a program's own mapped role.
#
# The API server (512MB instance) can't run sentence-transformers, so
# embeddings for every known skill phrase are precomputed offline by
# pipeline/build_skill_embeddings.py into skill_embeddings.npz and matching
# here is pure numpy. Skills missing from that file (added to the DB after
# the last rebuild) fall back to exact-string matching — degraded, not
# broken; rerun the build script after data refreshes.

_ROOT = Path(__file__).resolve().parents[1]
_SKILL_EMB_PATH = _ROOT / "data" / "processed" / "unified" / "skill_embeddings.npz"
_skill_emb_cache: tuple[dict, "np.ndarray"] | None = None


def _skill_embeddings() -> tuple[dict, "np.ndarray"]:
    global _skill_emb_cache
    if _skill_emb_cache is None:
        data = np.load(_SKILL_EMB_PATH, allow_pickle=True)
        names = list(data["names"])
        _skill_emb_cache = ({n: i for i, n in enumerate(names)}, data["embeddings"])
    return _skill_emb_cache


def semantic_covered_job_skills(prog_skills: set[str], job_skills: set[str]) -> set[str]:
    """Which job-side skills does the program cover? Same decision rule as
    pipeline/compute_alignment.py::compute_semantic_alignment's job_covered
    pass: best cosine >= 0.65 wins unless that specific (program skill, job
    skill) pair is blocklisted (then walk down the similarity ranking), with
    the allowlist as a below-threshold rescue."""
    from pipeline.compute_alignment import ALLOWLIST, BLOCKLIST, SIMILARITY_THRESHOLD

    idx, mat = _skill_embeddings()
    covered = {j for j in job_skills if j in prog_skills}

    prog_list = [s for s in prog_skills if s in idx]
    pending = [j for j in job_skills if j not in covered and j in idx]
    if prog_list and pending:
        prog_m = mat[[idx[s] for s in prog_list]]
        job_m = mat[[idx[s] for s in pending]]
        sims = job_m @ prog_m.T
        for row, j in enumerate(pending):
            for pi in np.argsort(sims[row])[::-1]:
                if sims[row][pi] < SIMILARITY_THRESHOLD:
                    break
                if (prog_list[pi], j) not in BLOCKLIST:
                    covered.add(j)
                    break

    for j in job_skills - covered:
        if any((p, j) in ALLOWLIST for p in prog_skills):
            covered.add(j)
    return covered


def compute_job_fit(
    program: str,
    degree: str,
    role_group: str,
    curriculum_df: pd.DataFrame,
    course_skills: dict,
    job_skills_by_role: dict,
    role_posting_counts: dict,
) -> dict:
    """Compare program skills against a specific role group (it_role_group
    labels, not the coarser relevant_roles taxonomy)."""
    from pipeline.compute_alignment import CORE_SKILL_FREQ_PCT

    prog_skills = get_program_skills(program, degree, curriculum_df, course_skills)
    role_counter: Counter = Counter(job_skills_by_role.get(role_group, {}))

    if not role_counter or not prog_skills:
        return {
            "match_score": None, "weighted_score": None, "matched": [], "missing": [],
            "n_core_skills": 0, "n_role_skills": len(role_counter),
            "n_program_skills": len(prog_skills), "n_role_postings": 0,
        }

    n_postings = role_posting_counts.get(role_group, 0)
    core_threshold = max(1, round(CORE_SKILL_FREQ_PCT * n_postings)) if n_postings else 1
    core = {s for s, c in role_counter.items() if c >= core_threshold}

    covered = semantic_covered_job_skills(prog_skills, set(role_counter))
    core_covered = covered & core

    match_score = len(core_covered) / len(core) * 100 if core else None
    core_total_weight = sum(role_counter[s] for s in core)
    weighted_score = (
        sum(role_counter[s] for s in core_covered) / core_total_weight * 100
        if core_total_weight else None
    )

    matched = sorted(
        [{"skill": s, "job_count": role_counter[s], "is_core": s in core} for s in covered],
        key=lambda x: -x["job_count"],
    )
    missing = sorted(
        [{"skill": s, "job_count": role_counter[s]} for s in core - core_covered],
        key=lambda x: -x["job_count"],
    )

    return {
        "match_score": match_score, "weighted_score": weighted_score,
        "matched": matched, "missing": missing,
        "n_core_skills": len(core), "n_role_skills": len(role_counter),
        "n_program_skills": len(prog_skills), "n_role_postings": n_postings,
    }
