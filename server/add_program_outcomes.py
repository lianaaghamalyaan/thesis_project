"""Create the program-outcomes tables and load source-backed outcomes.

The outcome layer is intentionally separate from ``course_skills``. It gives
users a transparent view of published program competencies without changing
any alignment score or implying that each competency is a course syllabus.

Usage (local pgAdmin database):
    ./.venv_dashboard/bin/python -m server.add_program_outcomes

Idempotent: re-running updates the source-backed NPUA outcome records rather
than inserting duplicates.
"""
from __future__ import annotations

from sqlalchemy import select

from .db import engine, get_session
from .models import Program, ProgramOutcome, ProgramOutcomeSkill, ProgramVersion, University


NPUA_SOFTWARE_ENGINEERING_SOURCE = "https://polytech.am/en/edu/software-engineering/#"

# Transcribed from the public English program page on 2026-07-14.  The skills
# below are conservative labels directly supported by each outcome statement.
NPUA_SOFTWARE_ENGINEERING_OUTCOMES = [
    (
        "To apply programming languages, knowledge of specific sections of mathematics in research and development of calculation systems and networks.",
        ["Applied Mathematics", "Computer Networks", "Computer Systems", "Programming Languages"],
    ),
    (
        "To apply knowledge of programming technologies of operational systems, computer networks and discrete structures for the development of calculation software.",
        ["Computer Networks", "Discrete Mathematics", "Operating Systems", "Programming Technologies", "Software Development"],
    ),
    (
        "To apply knowledge of operational systems, calculation network management and realization methods for the design and development of device and software of calculation systems and networks.",
        ["Computer Network Management", "Computer Networks", "Operating Systems", "Systems Design"],
    ),
    (
        "To acquire mathematical logics, development of device and software of calculation systems and networks, acquisition of toolset of systems analysis for the design and development of calculation systems and networks.",
        ["Mathematical Logic", "Software Development", "Systems Analysis", "Systems Design"],
    ),
    (
        "To acquire experience of scientific and research projects implementation.",
        ["Research Methods", "Scientific Research"],
    ),
]


def ensure_tables() -> None:
    """Create only the two new outcome tables; existing tables are untouched."""
    ProgramOutcome.__table__.create(engine, checkfirst=True)
    ProgramOutcomeSkill.__table__.create(engine, checkfirst=True)


def get_current_program_version(session) -> ProgramVersion:
    version = session.execute(
        select(ProgramVersion)
        .join(Program, ProgramVersion.program_id == Program.id)
        .join(University, Program.university_id == University.id)
        .where(
            University.name == "National Polytechnic University of Armenia",
            Program.name == "Software Engineering",
            Program.degree_level == "Master",
            ProgramVersion.is_current == True,  # noqa: E712
        )
    ).scalar_one()
    return version


def load_npua_software_engineering_outcomes() -> None:
    ensure_tables()
    session = get_session()
    try:
        version = get_current_program_version(session)
        for outcome_index, (outcome_text, skills) in enumerate(NPUA_SOFTWARE_ENGINEERING_OUTCOMES, start=1):
            outcome = session.execute(
                select(ProgramOutcome).where(
                    ProgramOutcome.program_version_id == version.id,
                    ProgramOutcome.outcome_index == outcome_index,
                )
            ).scalar_one_or_none()
            if outcome is None:
                outcome = ProgramOutcome(
                    program_version_id=version.id,
                    outcome_index=outcome_index,
                    outcome_text=outcome_text,
                    source_url=NPUA_SOFTWARE_ENGINEERING_SOURCE,
                    source_language="English",
                    is_official=True,
                )
                session.add(outcome)
                session.flush()
            else:
                outcome.outcome_text = outcome_text
                outcome.source_url = NPUA_SOFTWARE_ENGINEERING_SOURCE
                outcome.source_language = "English"
                outcome.is_official = True

            existing = {
                row[0]
                for row in session.execute(
                    select(ProgramOutcomeSkill.skill_name).where(ProgramOutcomeSkill.outcome_id == outcome.id)
                ).all()
            }
            for skill_name in skills:
                if skill_name not in existing:
                    session.add(ProgramOutcomeSkill(
                        outcome_id=outcome.id,
                        skill_name=skill_name,
                        extraction_method="source_text_review",
                    ))
        session.commit()
        print(f"Loaded {len(NPUA_SOFTWARE_ENGINEERING_OUTCOMES)} official outcomes for ProgramVersion {version.id}.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_npua_software_engineering_outcomes()
