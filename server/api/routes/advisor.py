"""AI curriculum advisor — given a market gap skill and a program, suggest
where and how to integrate it: the best-fit existing course, a concrete
module outline, and the employer-demand rationale drawn from real posting
evidence (never invented demand).

Gated to a university's own org_admin (require_curriculum_editor) and scoped
to that university's courses — same tenant boundary as My Curriculum. The
model only ever sees this program's own course list and the anonymized
job-posting evidence phrases for the one requested skill; it is asked to
choose among the real courses, not to invent new ones.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.db import SessionLocal
from server.models import (
    Course,
    JobPosting,
    JobSkillExtractionPosting,
    JobSkillExtractionRun,
    JobSkillExtractionSkill,
    Program,
    ProgramVersion,
    University,
)

from ..deps import require_curriculum_editor
from ..schemas import AdvisorRequest, AdvisorResponse

ROOT = Path(__file__).resolve().parents[3]

router = APIRouter(tags=["advisor"])

SYSTEM_PROMPT = """You are a curriculum advisor helping an Armenian university integrate a \
market-demanded technical skill into an existing degree program. You are given the skill, \
verbatim phrases from real job postings that demand it, and the program's actual course list \
with descriptions.

Recommend how to add the skill by extending ONE existing course (never invent a new course). \
Choose the single best-fit course from the list provided — the one whose topic is closest, so \
the addition is a natural extension rather than a bolt-on.

Respond with ONLY a JSON object, no prose around it:
{
  "best_course": "<exact course name from the list>",
  "why_this_course": "<1-2 sentences: why this course is the natural home>",
  "module_outline": ["<3-5 concise bullet topics to add>"],
  "employer_rationale": "<1-2 sentences summarizing what employers actually ask for, grounded in the evidence phrases>",
  "effort": "<one of: small (a lecture or two) | moderate (a multi-week module) | large (a new course unit)>"
}

Be concrete and realistic. Do not overstate. If none of the courses is a good fit, still pick \
the closest and say so honestly in why_this_course."""


def _db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _generate(prompt: str) -> str:
    """Call an LLM and return raw text. Gemini first (a free monthly tier),
    Anthropic as fallback if only that key is configured. Reads keys from
    the repo-root .env at call time so a running server picks up a newly
    added key without a code change."""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=gemini_key)
        # gemini-3.5-flash is a "thinking" model; leaving thinking on spends
        # the output budget on reasoning and truncates the JSON. Disable it
        # (thinking_budget=0) and give ample tokens so the object completes.
        cfg = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2048,
            response_mime_type="application/json",  # force clean JSON
            temperature=0.4,
        )
        try:
            cfg.thinking_config = types.ThinkingConfig(thinking_budget=0)
        except Exception:  # noqa: BLE001 — older SDKs / non-thinking models
            pass
        resp = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=prompt,
            config=cfg,
        )
        text = (resp.text or "").strip()
        if not text:
            raise ValueError("Gemini returned no text")
        return text

    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        msg = anthropic.Anthropic().messages.create(
            model="claude-sonnet-5",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
        if not parts:
            raise ValueError("Claude returned no text block")
        return "\n".join(parts).strip()

    raise ValueError("No LLM API key configured (set GEMINI_API_KEY or ANTHROPIC_API_KEY)")


@router.post("/advisor/integrate-skill", response_model=AdvisorResponse)
def integrate_skill(
    body: AdvisorRequest,
    user: dict = Depends(require_curriculum_editor),
    db: Session = Depends(_db),
) -> AdvisorResponse:
    university = user["university_name"]

    prog = (
        db.query(Program)
        .join(University, Program.university_id == University.id)
        .filter(University.name == university, Program.name == body.program, Program.degree_level == body.degree)
        .first()
    )
    if prog is None:
        raise HTTPException(404, "Program not found")

    version = (
        db.query(ProgramVersion)
        .filter(ProgramVersion.program_id == prog.id, ProgramVersion.is_current.is_(True))
        .first()
    )
    if version is None:
        raise HTTPException(404, "No current curriculum version")

    courses = db.query(Course).filter(Course.program_version_id == version.id).all()
    if not courses:
        raise HTTPException(404, "No courses to advise on")

    # Real employer-demand evidence for this skill, from the promoted run —
    # distinct phrases so the model sees breadth, not one posting repeated.
    run = (
        db.query(JobSkillExtractionRun)
        .filter(JobSkillExtractionRun.status == "completed")
        .order_by(JobSkillExtractionRun.created_at.desc())
        .first()
    )
    evidence: list[dict] = []
    n_postings = 0
    if run is not None:
        rows = (
            db.query(JobSkillExtractionSkill.evidence_text, JobPosting.it_role_group, JobPosting.company_name)
            .join(JobSkillExtractionPosting, JobSkillExtractionSkill.extraction_posting_id == JobSkillExtractionPosting.id)
            .join(JobPosting, JobSkillExtractionPosting.posting_id == JobPosting.id)
            .filter(
                JobSkillExtractionPosting.run_id == run.id,
                JobSkillExtractionSkill.normalized_skill_name == body.skill,
                JobPosting.is_active.is_(True),
            )
            .limit(200)
            .all()
        )
        n_postings = len({r.evidence_text for r in rows})
        seen: set[str] = set()
        for ev, role, _co in rows:
            key = ev.strip()[:200]
            if key and key not in seen:
                seen.add(key)
                evidence.append({"phrase": key, "role": role})
            if len(evidence) >= 10:
                break

    course_lines = "\n".join(
        f"- {c.name}"
        + (f" ({c.credits} credits)" if c.credits is not None else "")
        + (f": {c.description.strip()[:400]}" if c.description else ": (no published description)")
        for c in courses
    )
    evidence_lines = "\n".join(f'- "{e["phrase"]}"' + (f" [{e['role']}]" if e["role"] else "") for e in evidence) or "(no posting evidence available for this skill)"

    prompt = (
        f"Skill to integrate: {body.skill}\n"
        f"Program: {body.program} ({body.degree}) at {university}\n\n"
        f"What employers ask for (verbatim from job postings):\n{evidence_lines}\n\n"
        f"The program's current courses:\n{course_lines}\n"
    )

    try:
        raw = _generate(prompt)
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(raw)
    except Exception as e:  # noqa: BLE001 — surface a clean message, don't 500 opaquely
        raise HTTPException(502, f"Advisor unavailable: {e}")

    return AdvisorResponse(
        skill=body.skill,
        best_course=str(data.get("best_course", "")),
        why_this_course=str(data.get("why_this_course", "")),
        module_outline=[str(x) for x in data.get("module_outline", [])][:6],
        employer_rationale=str(data.get("employer_rationale", "")),
        effort=str(data.get("effort", "")),
        n_evidence_postings=n_postings,
    )
