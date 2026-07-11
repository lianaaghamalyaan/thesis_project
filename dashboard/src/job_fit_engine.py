from __future__ import annotations

from collections import Counter

from src.alignment import get_program_skills, ROLE_MAPPING


def compute_job_fit(
    program: str,
    degree: str,
    role_group: str,
    curriculum_df,
    course_skills: dict,
    job_skills_by_role: dict,
) -> dict:
    """
    Compare program skills against a specific role group (uses it_role_group labels).

    Returns:
        match_score: float (0-100), percentage of role skills covered by the program
        matched: list of dicts {skill, job_count} — skills in both
        missing: list of dicts {skill, job_count} — role skills absent from program
        n_role_skills: total unique skills demanded by this role
        n_program_skills: total skills extracted from the program
    """
    prog_skills = get_program_skills(program, degree, curriculum_df, course_skills)
    role_counter: Counter = job_skills_by_role.get(role_group, Counter())

    if not role_counter:
        return {
            "match_score": None,
            "matched": [],
            "missing": [],
            "n_role_skills": 0,
            "n_program_skills": len(prog_skills),
        }

    role_skills_set = set(role_counter.keys())
    matched_set = prog_skills & role_skills_set
    missing_set = role_skills_set - prog_skills

    match_score = len(matched_set) / len(role_skills_set) * 100

    matched = sorted(
        [{"skill": s, "job_count": role_counter[s]} for s in matched_set],
        key=lambda x: -x["job_count"],
    )
    missing = sorted(
        [{"skill": s, "job_count": role_counter[s]} for s in missing_set],
        key=lambda x: -x["job_count"],
    )

    return {
        "match_score": match_score,
        "matched": matched,
        "missing": missing,
        "n_role_skills": len(role_skills_set),
        "n_program_skills": len(prog_skills),
    }
