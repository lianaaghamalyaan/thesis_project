"""SQLAlchemy models for CurriculumLens.

Design principles (from docs/product/data_pipeline_architecture.md and
system_architecture_plan.md §9):
- All universities share one database; visibility is filtered at query time
  by the logged-in organization, never by physical separation.
- Nothing is deleted: job postings are marked inactive, curriculum changes
  create new program versions, alignment reruns create new run rows.
- Every analysis row points to the run that produced it, so history stays
  queryable after refreshes.
"""
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Tenancy & auth ──────────────────────────────────────────────────────────

class Organization(Base):
    """Who logs in: a university, a policy body, or the platform operator."""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    # university → sees only its own university's programs
    # policy     → sees all universities, named (ministry / ANQA / donors)
    # internal   → platform operator, sees everything + admin
    org_type: Mapped[str] = mapped_column(String(20))
    university_id: Mapped[int | None] = mapped_column(
        ForeignKey("universities.id"), nullable=True
    )  # set only for org_type='university'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))  # pbkdf2:iterations:salt:hash
    full_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(20), default="viewer")  # org_admin | viewer | superadmin
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="users")


# ── Curriculum side ─────────────────────────────────────────────────────────

class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    short_name: Mapped[str] = mapped_column(String(50), default="")
    country: Mapped[str] = mapped_column(String(50), default="Armenia")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    programs: Mapped[list["Program"]] = relationship(back_populates="university")


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (
        UniqueConstraint("university_id", "name", "degree_level", name="uq_program"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(300))
    degree_level: Mapped[str] = mapped_column(String(30))  # Bachelor | Master | General
    program_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    relevant_roles: Mapped[str | None] = mapped_column(String(300), nullable=True)  # comma-separated role groups, or 'ALL'
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # where the curriculum was scraped from (refresh target)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    university: Mapped["University"] = relationship(back_populates="programs")
    versions: Mapped[list["ProgramVersion"]] = relationship(back_populates="program")


class ProgramVersion(Base):
    """A snapshot of a program's curriculum at a point in time.

    Created when curriculum data is (re)collected — target cadence: every 6
    months. If nothing changed (same content hash), no new version is made.
    Courses hang off a version, so history is fully preserved.
    """
    __tablename__ = "program_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    collected_at: Mapped[date] = mapped_column(Date)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # sha256 over ordered course content; refresh skips if unchanged
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped["Program"] = relationship(back_populates="versions")
    courses: Mapped[list["Course"]] = relationship(back_populates="program_version")
    outcomes: Mapped[list["ProgramOutcome"]] = relationship(back_populates="program_version")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_version_id: Mapped[int] = mapped_column(ForeignKey("program_versions.id"))
    course_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(500))
    name_original: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    credits: Mapped[float | None] = mapped_column(Float, nullable=True)
    semester: Mapped[str | None] = mapped_column(String(20), nullable=True)  # free-text: universities encode this inconsistently ("1.0", "1/autumn", "9/M2-S1")
    source_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    program_version: Mapped["ProgramVersion"] = relationship(back_populates="courses")
    skills: Mapped[list["CourseSkill"]] = relationship(back_populates="course")


class CourseSkill(Base):
    """LLM-extracted skill evidenced by a course. confidence_tier powers the
    documentation-gap signal (low confidence = thin description)."""
    __tablename__ = "course_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    skill_name: Mapped[str] = mapped_column(String(300))
    confidence_tier: Mapped[str | None] = mapped_column(String(10), nullable=True)  # high | medium | low
    extraction_method: Mapped[str] = mapped_column(String(20), default="LLM")
    input_type: Mapped[str] = mapped_column(String(20), default="names")  # names | descriptions

    course: Mapped["Course"] = relationship(back_populates="skills")


class ProgramOutcome(Base):
    """An official, program-level learning outcome kept separate from courses.

    Outcomes are useful evidence for visitors, but they do not enter the
    alignment calculation until their treatment is explicitly validated.
    """
    __tablename__ = "program_outcomes"
    __table_args__ = (
        UniqueConstraint("program_version_id", "outcome_index", name="uq_program_outcome_index"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    program_version_id: Mapped[int] = mapped_column(ForeignKey("program_versions.id"))
    outcome_index: Mapped[int] = mapped_column(Integer)
    outcome_text: Mapped[str] = mapped_column(Text)
    outcome_text_original: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    program_version: Mapped["ProgramVersion"] = relationship(back_populates="outcomes")
    skills: Mapped[list["ProgramOutcomeSkill"]] = relationship(back_populates="outcome")


class ProgramOutcomeSkill(Base):
    """A skill extracted from a specific program-level outcome statement."""
    __tablename__ = "program_outcome_skills"
    __table_args__ = (
        UniqueConstraint("outcome_id", "skill_name", name="uq_program_outcome_skill"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    outcome_id: Mapped[int] = mapped_column(ForeignKey("program_outcomes.id"))
    skill_name: Mapped[str] = mapped_column(String(300))
    extraction_method: Mapped[str] = mapped_column(String(30), default="LLM")

    outcome: Mapped["ProgramOutcome"] = relationship(back_populates="skills")


# ── Job market side ─────────────────────────────────────────────────────────

class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    source_type: Mapped[str] = mapped_column(String(30), default="company_portal")  # aggregator | company_portal | job_board
    url: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobCollection(Base):
    """One scraping run per source — the freshness audit trail."""
    __tablename__ = "job_collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("job_sources.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    n_collected: Mapped[int] = mapped_column(Integer, default=0)
    n_new: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="success")  # success | partial | failed
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(16), unique=True)  # sha1(source_url)[:16] — stable across refreshes
    source_id: Mapped[int] = mapped_column(ForeignKey("job_sources.id"))
    source_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(500))
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_it_job: Mapped[bool] = mapped_column(Boolean, default=True)
    it_role_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Postings unseen for >6 months are marked inactive (never deleted) and
    # drop out of the "current market" used for analysis.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    skills: Mapped[list["JobSkill"]] = relationship(back_populates="posting")


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (
        UniqueConstraint("posting_id", "skill_name", name="uq_job_skill"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"))
    skill_name: Mapped[str] = mapped_column(String(300))
    extraction_method: Mapped[str] = mapped_column(String(20), default="LLM")
    prompt_version: Mapped[str | None] = mapped_column(String(60), nullable=True)

    posting: Mapped["JobPosting"] = relationship(back_populates="skills")


class JobSkillExtractionRun(Base):
    """An auditable, non-destructive job-skill extraction run.

    Historical ``job_skills`` remains the score-bearing data until a run has
    been reviewed and explicitly promoted through a separate process.
    """
    __tablename__ = "job_skill_extraction_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_key: Mapped[str] = mapped_column(String(80), unique=True)
    model_name: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="running")
    expected_postings: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    postings: Mapped[list["JobSkillExtractionPosting"]] = relationship(back_populates="run")


class JobSkillExtractionPosting(Base):
    """One posting processed in a versioned job-skill extraction run."""
    __tablename__ = "job_skill_extraction_postings"
    __table_args__ = (
        UniqueConstraint("run_id", "posting_id", name="uq_job_skill_run_posting"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("job_skill_extraction_runs.id"))
    posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"))
    input_hash: Mapped[str] = mapped_column(String(64))
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run: Mapped["JobSkillExtractionRun"] = relationship(back_populates="postings")
    skills: Mapped[list["JobSkillExtractionSkill"]] = relationship(back_populates="extraction_posting")


class JobSkillExtractionSkill(Base):
    """A raw and normalized skill with an evidence quote from the posting."""
    __tablename__ = "job_skill_extraction_skills"
    __table_args__ = (
        UniqueConstraint(
            "extraction_posting_id", "normalized_skill_name", name="uq_job_extraction_skill"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    extraction_posting_id: Mapped[int] = mapped_column(
        ForeignKey("job_skill_extraction_postings.id")
    )
    raw_skill_name: Mapped[str] = mapped_column(String(300))
    normalized_skill_name: Mapped[str] = mapped_column(String(300))
    evidence_text: Mapped[str] = mapped_column(Text)
    evidence_type: Mapped[str] = mapped_column(String(20), default="explicit")

    extraction_posting: Mapped["JobSkillExtractionPosting"] = relationship(back_populates="skills")


# ── Analysis side ───────────────────────────────────────────────────────────

class AlignmentRun(Base):
    __tablename__ = "alignment_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_key: Mapped[str] = mapped_column(String(60), unique=True)  # e.g. 'march_2026_static', '2026-07-25'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    experiment: Mapped[str] = mapped_column(String(60), default="LLM_desc_semantic")
    esco_version: Mapped[str] = mapped_column(String(20), default="v1.2")
    job_snapshot_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    n_active_postings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=False)  # what the dashboard shows
    status: Mapped[str] = mapped_column(String(20), default="complete")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    results: Mapped[list["AlignmentResult"]] = relationship(back_populates="run")


class AlignmentResult(Base):
    __tablename__ = "alignment_results"
    __table_args__ = (
        UniqueConstraint("run_id", "program_id", name="uq_run_program"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("alignment_runs.id"))
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    program_version_id: Mapped[int | None] = mapped_column(ForeignKey("program_versions.id"), nullable=True)
    n_program_skills: Mapped[int | None] = mapped_column(Integer, nullable=True)
    n_job_skills: Mapped[int | None] = mapped_column(Integer, nullable=True)
    n_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    full_coverage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    role_coverage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    core_role_coverage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    core_n_job_skills: Mapped[int | None] = mapped_column(Integer, nullable=True)
    core_n_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    core_n_gap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weighted_core_coverage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    run: Mapped["AlignmentRun"] = relationship(back_populates="results")
    gap_skills: Mapped[list["GapSkill"]] = relationship(back_populates="result")


class GapSkill(Base):
    __tablename__ = "gap_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("alignment_results.id"))
    skill_name: Mapped[str] = mapped_column(String(300))
    job_frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. 'DevOps & Cloud' (from LLM gap analysis)
    gap_type: Mapped[str | None] = mapped_column(String(30), nullable=True)  # curriculum_gap | documentation_gap | uncertain

    result: Mapped["AlignmentResult"] = relationship(back_populates="gap_skills")


class SkillInfo(Base):
    """One-line plain-English context for a skill name shown anywhere on the
    dashboard — CLAUDE.md's target users are non-technical academic
    leadership who "need to understand outcomes, not methodology"; a bare
    tool name like "TypeScript" or "CI/CD" in a gap list doesn't tell a
    vice-rector what it is. Generated once per skill
    (pipeline/generate_skill_info.py, Claude Haiku) and cached here — never
    regenerated live, since the answer for a given skill name doesn't change.
    """
    __tablename__ = "skill_info"

    skill_name: Mapped[str] = mapped_column(String(300), primary_key=True)
    description: Mapped[str] = mapped_column(Text)  # one sentence: what it is
    where_used: Mapped[str] = mapped_column(String(200))  # short phrase: e.g. "Web frontend development"
    model_used: Mapped[str] = mapped_column(String(60))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
