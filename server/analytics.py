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

from .role_mapping import expand_program_roles

MIN_ROLE_MATCHED_PEERS = 3


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


def _get_core_job_skills_for_roles(role_set: set[str], job_skills_by_role: dict, role_posting_counts: dict) -> set[str]:
    """Same per-role "core" definition as pipeline/compute_alignment.py's
    get_core_job_skills: a skill counts as core for a role if it appears in
    >= 5% of THAT role's own postings, and a multi-role program's core set
    is the UNION of each role's core set (not a threshold on the combined
    count) — a skill can be core for one of a program's roles even if it
    wouldn't clear 5% of the roles' postings pooled together."""
    from pipeline.compute_alignment import CORE_SKILL_FREQ_PCT

    out: set[str] = set()
    for role in role_set:
        n_postings = role_posting_counts.get(role, 0)
        if n_postings == 0:
            continue
        min_count = max(1, round(CORE_SKILL_FREQ_PCT * n_postings))
        out |= {s for s, c in job_skills_by_role.get(role, {}).items() if c >= min_count}
    return out


def _get_role_freq_map(role_set: set[str], job_skills_by_role: dict) -> Counter:
    """Same combined-frequency definition as compute_alignment.py's
    get_freq_map: a skill's displayed job_count is its posting count summed
    across every one of the program's resolved roles, not just the role
    that made it core."""
    combined: Counter = Counter()
    for role in role_set:
        for skill, count in job_skills_by_role.get(role, {}).items():
            combined[skill] += count
    return combined


def get_strengths(
    program: str,
    degree: str,
    relevant_roles: str | None,
    curriculum_df: pd.DataFrame,
    course_skills: dict,
    job_skills_by_role: dict,
    role_posting_counts: dict,
    n: int = 20,
) -> list[dict]:
    """The program's core skills (same definition the headline
    core_role_coverage_pct is computed from) that the program's own
    curriculum covers, via the same bidirectional semantic matching used
    everywhere else (semantic_covered_job_skills_with_source) — not exact
    string equality against every skill ever mentioned for the role. This
    is what makes "Covers N of M core skills" (compute_alignment.py) and
    the Strengths list shown on the same page describe the same N, instead
    of two independently-computed numbers that a careful reader couldn't
    reconcile."""
    known_roles = set(job_skills_by_role.keys())
    role_set = expand_program_roles(relevant_roles, known_roles)
    if not role_set:
        return []

    prog_skills = get_program_skills(program, degree, curriculum_df, course_skills)
    core_skills = _get_core_job_skills_for_roles(role_set, job_skills_by_role, role_posting_counts)
    freq_map = _get_role_freq_map(role_set, job_skills_by_role)

    covered = semantic_covered_job_skills_with_source(prog_skills, core_skills)
    matched = [
        {"skill": job_skill, "job_count": freq_map.get(job_skill, 0), "matched_program_skills": sources}
        for job_skill, sources in covered.items()
    ]
    matched.sort(key=lambda x: -x["job_count"])
    return matched[:n]


SHORT_DESCRIPTION_CHARS = 50  # matches the existing "missing_descriptions" threshold in admin/doc-quality


def classify_course_description(description: object, notes: object) -> str:
    """One of "missing" (nothing published), "ai_generated" (no real
    description existed — an AI one was generated from the course name/program
    context so the course could still be analyzed), "short" (a real but
    thin description), or "full"."""
    has_notes = isinstance(notes, str) and "AI-generated" in notes
    if has_notes:
        return "ai_generated"
    if not isinstance(description, str) or not description.strip():
        return "missing"
    if len(description) < SHORT_DESCRIPTION_CHARS:
        return "short"
    return "full"


def program_documentation_breakdown(program: str, degree: str, curriculum_df: pd.DataFrame) -> dict:
    """How much of this program's curriculum data is actually published by
    the university, vs. missing or AI-filled-in. Distinct from doc_score
    (which measures skill-extraction confidence) — this measures what raw
    material existed in the first place."""
    courses = curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]
    counts = {"missing": 0, "ai_generated": 0, "short": 0, "full": 0}
    for _, row in courses.iterrows():
        counts[classify_course_description(row.get("description"), row.get("notes"))] += 1

    n = len(courses)
    no_real_data = counts["missing"] + counts["ai_generated"]
    pct_no_real_data = no_real_data / n if n else 0.0

    pct_thin_or_missing = pct_no_real_data + (counts["short"] / n if n else 0)
    if n == 0 or pct_no_real_data >= 0.9:
        level = "no_published_data"
    elif pct_no_real_data >= 0.5 or pct_thin_or_missing >= 0.75:
        level = "minimal"
    elif no_real_data > 0 or counts["short"] > 0:
        level = "partial"
    else:
        level = "full"

    return {"n_courses": n, **counts, "pct_no_real_data": pct_no_real_data, "level": level}


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
    dashboard/src/benchmark.py's load_all_universities_alignment(). Compares
    on weighted_core_coverage_pct, the headline metric — see
    pipeline/compute_alignment.py's docstring for why."""
    others = all_alignment[
        (all_alignment["university"] != university)
        & (all_alignment["degree"] == degree)
        & (all_alignment["weighted_core_coverage_pct"].notna())
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
        "peer_mean": float(others["weighted_core_coverage_pct"].mean()),
        "peer_median": float(others["weighted_core_coverage_pct"].median()),
        "peer_max": float(others["weighted_core_coverage_pct"].max()),
        "peer_n": int(len(others)),
        "matched_on": matched_on,
    }


def get_program_recommendations(
    program: str,
    degree: str,
    headline_score: float | None,
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

    if headline_score is not None and not pd.isna(headline_score) and headline_score < 25:
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


def semantic_covered_job_skills_with_source(prog_skills: set[str], job_skills: set[str]) -> dict[str, list[str]]:
    """Which job-side skills does the program cover, and which of the
    program's own skill(s) justified each one? Same decision rule as
    pipeline/compute_alignment.py::compute_semantic_alignment's job_covered
    pass: best cosine >= 0.65 wins unless that specific (program skill, job
    skill) pair is blocklisted (then walk down the similarity ranking), with
    the allowlist as a below-threshold rescue. Returning the source program
    skill(s) (not just a boolean) is what lets a Strengths row whose
    job-market wording differs from the program's own wording (e.g. program
    teaches "Distributed Computing Systems", the market calls it
    "Distributed Systems") still point "how was this decided?" at the real
    course, instead of failing to find one under an exact-name lookup."""
    from pipeline.compute_alignment import ALLOWLIST, BLOCKLIST, SIMILARITY_THRESHOLD

    idx, mat = _skill_embeddings()
    covered: dict[str, list[str]] = {j: [j] for j in job_skills if j in prog_skills}

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
                    covered[j] = [prog_list[pi]]
                    break

    for j in job_skills - covered.keys():
        sources = [p for p in prog_skills if (p, j) in ALLOWLIST]
        if sources:
            covered[j] = sources
    return covered


def semantic_covered_job_skills(prog_skills: set[str], job_skills: set[str]) -> set[str]:
    """Which job-side skills does the program cover — see
    semantic_covered_job_skills_with_source for the decision rule. This is
    the set-only view used where the matching program skill doesn't matter
    (e.g. Job Fit's score, which only needs coverage counts)."""
    return set(semantic_covered_job_skills_with_source(prog_skills, job_skills).keys())


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
