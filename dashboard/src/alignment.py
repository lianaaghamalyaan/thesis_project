from __future__ import annotations

import pandas as pd
from collections import Counter


# Role name mappings between alignment relevant_roles and jobs it_role_group labels
# alignment uses broader categories; jobs use finer labels
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


def expand_roles(relevant_roles: str) -> list[str]:
    """Map alignment role group strings to it_role_group labels used in job data."""
    if not relevant_roles or str(relevant_roles) in ("unmapped", "nan", ""):
        return []
    job_roles = []
    for r in str(relevant_roles).split(","):
        r = r.strip()
        job_roles.extend(ROLE_MAPPING.get(r, [r]))
    return list(dict.fromkeys(job_roles))  # deduplicated, order-preserving


def get_program_skills(program: str, degree: str, curriculum_df, course_skills: dict) -> set:
    """Return the union of all skills extracted from a program's courses."""
    courses = curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]
    skills: set = set()
    for _, row in courses.iterrows():
        course_id = str(int(row["course_id"]))
        skills.update(course_skills.get(course_id, []))
    return skills


def get_role_skill_counter(relevant_roles: str, job_skills_by_role: dict) -> Counter:
    """Aggregate skill counts across all relevant job-side role groups."""
    job_roles = expand_roles(relevant_roles)
    agg: Counter = Counter()
    for role in job_roles:
        agg.update(job_skills_by_role.get(role, {}))
    return agg


def get_strengths(
    program: str,
    degree: str,
    relevant_roles: str,
    curriculum_df,
    course_skills: dict,
    job_skills_by_role: dict,
    n: int = 20,
) -> list[dict]:
    """
    Return up to n skills that the program covers AND appear in market demand
    for its relevant roles. Each dict has: skill, job_count.
    """
    prog_skills = get_program_skills(program, degree, curriculum_df, course_skills)
    role_counter = get_role_skill_counter(relevant_roles, job_skills_by_role)

    matched = [
        {"skill": s, "job_count": role_counter[s]}
        for s in prog_skills
        if s in role_counter
    ]
    matched.sort(key=lambda x: -x["job_count"])
    return matched[:n]
