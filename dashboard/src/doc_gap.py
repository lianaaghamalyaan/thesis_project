from __future__ import annotations


def compute_program_doc_score(
    program: str,
    degree: str,
    curriculum_df,
    tiers: dict,
) -> float:
    """
    Compute a documentation quality score for a program (0–1).

    High score: courses have detailed, explicit descriptions → extracted skills are reliable
    → gaps are likely real curriculum gaps.

    Low score: course descriptions are vague or missing → extraction was limited
    → gaps may be documentation gaps rather than real curriculum gaps.
    """
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
    """
    Classify whether gaps for this program are likely curriculum or documentation gaps.
    Based on how well the program's courses are documented.
    """
    if doc_score >= 0.45:
        return "curriculum_gap"
    if doc_score <= 0.20:
        return "documentation_gap"
    return "uncertain"


def annotate_gaps(gaps_df, program: str, degree: str, curriculum_df, tiers: dict):
    """
    Return a copy of the gaps_df slice for this program with gap_type, doc_score columns.
    """
    doc_score = compute_program_doc_score(program, degree, curriculum_df, tiers)
    gap_type = classify_gap_type(doc_score)

    prog_gaps = gaps_df[
        (gaps_df["program"] == program) & (gaps_df["degree"] == degree)
    ].copy()
    prog_gaps["gap_type"] = gap_type
    prog_gaps["doc_score"] = doc_score
    return prog_gaps, doc_score, gap_type
