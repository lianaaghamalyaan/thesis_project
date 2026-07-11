from __future__ import annotations

import pandas as pd

from src.doc_gap import annotate_gaps, compute_program_doc_score


def get_program_recommendations(
    program: str,
    degree: str,
    alignment_row,
    gaps_df: pd.DataFrame,
    curriculum_df,
    tiers: dict,
) -> list[dict]:
    """
    Generate 3–5 actionable recommendations for a program.
    Each recommendation is a dict: {type, title, description, priority}.
    """
    recs = []

    doc_score = compute_program_doc_score(program, degree, curriculum_df, tiers)
    _, _, gap_type = annotate_gaps(gaps_df, program, degree, curriculum_df, tiers)

    prog_gaps = gaps_df[
        (gaps_df["program"] == program) & (gaps_df["degree"] == degree)
    ].sort_values("job_frequency", ascending=False)

    score = getattr(alignment_row, "core_role_coverage_pct", None)

    # 1. Documentation quality recommendation
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

    # 2. Top gap skills
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

    # 3. Score context
    if score is not None and not pd.isna(score) and score < 25:
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

    # 4. Caveat note
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
    """
    Return top gap skills that appear across the most programs,
    useful for identifying university-wide priorities.
    """
    if gaps_df.empty:
        return pd.DataFrame()

    agg = (
        gaps_df.groupby("gap_skill")
        .agg(n_programs=("program", "nunique"), total_frequency=("job_frequency", "sum"))
        .reset_index()
        .sort_values(["n_programs", "total_frequency"], ascending=[False, False])
    )
    return agg.head(25)
