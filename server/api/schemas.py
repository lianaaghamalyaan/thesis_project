"""Pydantic response models, mirroring server/queries.py's DataFrame shapes.

Kept deliberately close to the DataFrame column names so the mapping from
queries.py -> API response is a straight `.to_dict("records")` pass, not a
reshaping exercise.
"""
from __future__ import annotations

from pydantic import BaseModel


class ProgramAlignment(BaseModel):
    experiment: str
    university: str
    program: str
    degree: str
    relevant_roles: str | None
    source_url: str | None
    n_program_skills: int | None
    n_job_skills: int | None
    n_overlap: int | None
    full_coverage_pct: float | None
    role_coverage_pct: float | None
    core_role_coverage_pct: float | None
    core_n_job_skills: int | None
    core_n_overlap: int | None
    core_n_gap: int | None
    weighted_core_coverage_pct: float | None


class GapSkillRow(BaseModel):
    university: str
    program: str
    degree: str
    gap_skill: str
    job_frequency: int | None
    relevant_roles: str | None


class LlmGapSkillRow(BaseModel):
    university: str
    program_name: str
    degree_level: str
    role_groups: str | None
    missing_skill: str
    job_frequency: int | None
    category: str | None


class CurriculumCourse(BaseModel):
    course_id: int
    university: str
    program_name: str
    degree_level: str
    course_code: str | None
    course_name: str
    course_name_original: str | None
    credits: float | None
    semester: str | None
    description: str | None
    source_language: str | None
    notes: str | None
    source_url: str | None
    academic_year: str | None


class JobSnapshot(BaseModel):
    collected_at: str | None
    n_it_postings: int | None
    n_sources: int | None
    window: str | None


class CurriculumSnapshot(BaseModel):
    collected_at: str | None
    n_universities: int | None
    n_programs: int | None
    n_courses: int | None


class RunMetadata(BaseModel):
    run_id: str
    is_canonical: bool
    experiment: str
    created_at: str
    curriculum_snapshot: CurriculumSnapshot
    job_snapshot: JobSnapshot
    esco_version: str | None
    notes: str | None


class BenchmarkResult(BaseModel):
    peer_mean: float
    peer_median: float
    peer_max: float
    peer_n: int
    matched_on: str


class StrengthSkill(BaseModel):
    skill: str
    job_count: int


class SkillCourse(BaseModel):
    course_name: str
    high_confidence: bool


class ProgramDetail(BaseModel):
    """Bundle for the Program Detail page — replaces the 7 separate loader
    calls dashboard/pages/program_detail.py used to make."""
    alignment: ProgramAlignment | None
    gaps: list[LlmGapSkillRow]
    fallback_gaps: list[GapSkillRow]
    strengths: list[StrengthSkill]
    skill_courses: dict[str, list[SkillCourse]]
    benchmark: BenchmarkResult | None
    doc_score: float
    gap_type: str
