"""Data access for the dashboard pages.

As of 2026-07-11 this reads from the Postgres database (server/queries.py)
instead of flat CSV/JSON files, scoped to the logged-in session's current
university (dashboard/src/auth_ui.py). Function names and return shapes are
unchanged from the CSV-era version so pages/*.py did not need to change.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from server import queries
from src.auth_ui import current_university


@st.cache_data(show_spinner=False)
def _cached_curriculum(university):
    return queries.load_curriculum(university)


def load_curriculum():
    return _cached_curriculum(current_university())


@st.cache_data(show_spinner=False)
def _cached_alignment(university):
    return queries.load_alignment(university)


def load_alignment():
    return _cached_alignment(current_university())


@st.cache_data(show_spinner=False)
def _cached_gaps(university):
    return queries.load_gaps(university)


def load_gaps():
    return _cached_gaps(current_university())


@st.cache_data(show_spinner=False)
def _cached_llm_gaps(university):
    return queries.load_llm_gaps(university)


def load_llm_gaps():
    return _cached_llm_gaps(current_university())


@st.cache_data(show_spinner=False)
def _cached_course_skills(university):
    return queries.load_course_skills(university)


def load_course_skills():
    """Load normalized course skills (names-only, canonical form)."""
    return _cached_course_skills(current_university())


@st.cache_data(show_spinner=False)
def _cached_confidence_tiers(university):
    return queries.load_confidence_tiers(university)


def load_confidence_tiers():
    return _cached_confidence_tiers(current_university())


@st.cache_data(show_spinner=False)
def load_job_skills_by_role() -> dict:
    """
    role -> Counter(skill -> job_count). National job-market data — the same
    for every session regardless of which university is being viewed.

    Coverage is currently partial: only postings that have been through LLM
    skill extraction have skills. Call job_skills_coverage() to check/display
    how much of the job set is covered.
    """
    return queries.load_job_skills_by_role()


@st.cache_data(show_spinner=False)
def job_skills_coverage() -> dict:
    """How many postings have LLM-extracted skill data vs. total, for an honest UI disclaimer."""
    return queries.job_skills_coverage()


@st.cache_data(show_spinner=False)
def load_run_metadata():
    return queries.load_run_metadata()


def get_program_courses(curriculum_df, program, degree):
    return curriculum_df[
        (curriculum_df["program_name"] == program) & (curriculum_df["degree_level"] == degree)
    ]


def list_programs(alignment_df):
    """Return list of (program, degree) tuples sorted by score descending."""
    df = alignment_df[["program", "degree", "core_role_coverage_pct"]].copy()
    df = df.sort_values("core_role_coverage_pct", ascending=False, na_position="last")
    return list(df.itertuples(index=False, name=None))
