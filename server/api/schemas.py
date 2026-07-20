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
    pct_of_role_postings: float | None = None


class LlmGapSkillRow(BaseModel):
    university: str
    program_name: str
    degree_level: str
    role_groups: str | None
    missing_skill: str
    job_frequency: int | None
    category: str | None
    pct_of_role_postings: float | None = None


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
    collected_at: str | None  # most recent posting_date among active postings
    earliest_at: str | None  # oldest posting_date among active postings
    n_it_postings: int | None
    n_sources: int | None
    n_unknown_date: int | None  # active postings with no posting_date on file
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
    pct_of_role_postings: float | None = None
    matched_program_skills: list[str] = []


class SkillCourse(BaseModel):
    course_name: str
    high_confidence: bool


class ExtractedSkillEvidence(BaseModel):
    skill_name: str
    confidence_tier: str | None = None
    extraction_method: str
    input_type: str | None = None


class CourseEvidence(BaseModel):
    course_name: str
    course_name_original: str | None
    credits: float | None
    description: str | None
    source_url: str | None
    source_language: str | None
    notes: str | None
    skills: list[ExtractedSkillEvidence]


class ProgramOutcomeEvidence(BaseModel):
    outcome_text: str
    outcome_text_original: str | None
    source_url: str | None
    source_language: str | None
    is_official: bool
    skills: list[ExtractedSkillEvidence]


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
    course_evidence: list[CourseEvidence]
    program_outcomes: list[ProgramOutcomeEvidence]


# ── "My Curriculum" editor (university admins confirming taught skills) ───

class SkillAssertion(BaseModel):
    id: int
    skill_name: str
    asserted_by: str
    asserted_at: str
    evidence_note: str | None


class EditorCourse(BaseModel):
    course_id: int
    course_name: str
    extracted_skills: list[str]
    assertions: list[SkillAssertion]


class EditorProgram(BaseModel):
    program: str
    degree: str
    courses: list[EditorCourse]


class CreateAssertionRequest(BaseModel):
    course_id: int
    skill_name: str
    evidence_note: str | None = None


class CoveragePreview(BaseModel):
    """Same shape twice — current (the stored canonical AlignmentResult, i.e.
    the exact headline shown everywhere else in the app) and with_assertions
    (that same baseline plus the live-computed increment from this
    university's confirmed-taught skills) — so the UI can show a trustworthy
    delta whose baseline can't disagree with the official score. Deliberately
    not written back to AlignmentResult; see CourseSkillAssertion's docstring
    for why the two stay separate, and curriculum_editor._project() for how
    the increment is anchored to the stored level."""
    core_n_job_skills: int | None
    current_core_n_overlap: int | None
    current_core_role_coverage_pct: float | None
    current_weighted_core_coverage_pct: float | None
    with_assertions_core_n_overlap: int | None
    with_assertions_core_role_coverage_pct: float | None
    with_assertions_weighted_core_coverage_pct: float | None
