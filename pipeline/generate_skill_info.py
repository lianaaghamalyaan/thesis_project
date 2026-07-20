"""Generate a one-line "what is this / where is it used" blurb for every
skill name currently in course_skills or job_skills, cached in the new
skill_info table (server/models.py::SkillInfo). CLAUDE.md's target users are
non-technical academic leadership — a bare skill name like "CI/CD" or
"TypeScript" in a Strengths/Gaps list means nothing to someone who isn't a
developer; this is what the "ⓘ" next to each skill name reads from.

Idempotent and incremental: only generates for skill names not already in
skill_info, so re-running after a scrape/consolidation cycle only costs
tokens for genuinely new skill names (typically a handful per week, not the
whole vocabulary) — safe to add as a step in the weekly refresh later.

Batches BATCH_SIZE skill names per API call (one sentence each needs very
little context, so batching keeps this cheap even for the full ~10k-skill
vocabulary on first run).

Requires ANTHROPIC_API_KEY in the environment.

Usage:
    DATABASE_URL=... ANTHROPIC_API_KEY=... ./.venv_dashboard/bin/python -m pipeline.generate_skill_info [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 25

SYSTEM_PROMPT = """You are writing short, plain-English explanations of technical skills for \
non-technical university leadership (vice-rectors, curriculum committees) who have no \
programming background. For each skill name given, write:

1. "description": ONE sentence explaining what it is, in plain language a non-technical \
reader can understand. No jargon in the explanation itself. If the skill IS itself a common \
plain-English term (e.g. "Communication", "Project Management"), still explain what it means \
in an IT job context.
2. "where_used": a short phrase (3-6 words) naming the area of software/IT work this is used \
in, e.g. "Web frontend development", "Cloud infrastructure and deployment", "Data analysis and reporting".

Return ONLY a JSON object mapping each exact input skill name to {"description": ..., "where_used": ...}. \
No other text."""


def message_text(message) -> str:
    parts = [block.text for block in message.content if getattr(block, "type", None) == "text"]
    return "\n".join(parts).strip()


def parse_response(raw: str) -> dict[str, dict[str, str]]:
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    payload = json.loads(raw)
    out: dict[str, dict[str, str]] = {}
    if not isinstance(payload, dict):
        return out
    for skill, info in payload.items():
        if isinstance(info, dict) and info.get("description") and info.get("where_used"):
            out[skill] = {"description": str(info["description"]).strip(), "where_used": str(info["where_used"]).strip()}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    from sqlalchemy import text

    from server.db import SessionLocal, engine
    from server.models import SkillInfo

    SkillInfo.__table__.create(engine, checkfirst=True)

    session = SessionLocal()
    try:
        all_skills = sorted({
            r[0] for r in session.execute(text(
                "SELECT DISTINCT skill_name FROM course_skills UNION SELECT DISTINCT skill_name FROM job_skills"
            )).all()
        })
        existing = {r[0] for r in session.execute(text("SELECT skill_name FROM skill_info")).all()}
        missing = [s for s in all_skills if s not in existing]
        if args.limit:
            missing = missing[: args.limit]

        print(f"{len(all_skills)} distinct skills total, {len(existing)} already have info, "
              f"{len(missing)} to generate.")
        if not missing:
            return
        if args.dry_run:
            print("Dry run — no writes. Sample:", missing[:10])
            return

        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set. Required for skill-info generation.")

        import anthropic
        client = anthropic.Anthropic()

        n_done = 0
        for i in range(0, len(missing), BATCH_SIZE):
            batch = missing[i : i + BATCH_SIZE]
            prompt = "Skills:\n" + "\n".join(f"- {s}" for s in batch)
            for attempt in range(3):
                try:
                    response = client.messages.create(
                        model=MODEL, max_tokens=2000, system=SYSTEM_PROMPT,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    results = parse_response(message_text(response))
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  batch {i // BATCH_SIZE}: attempt {attempt + 1} failed: {e}", file=sys.stderr)
                    time.sleep(2 ** attempt)
                    results = {}
            for skill in batch:
                info = results.get(skill)
                if not info:
                    print(f"  WARNING: no info returned for {skill!r}, skipping (will retry next run).",
                          file=sys.stderr)
                    continue
                session.add(SkillInfo(
                    skill_name=skill, description=info["description"], where_used=info["where_used"],
                    model_used=MODEL,
                ))
                n_done += 1
            session.commit()
            print(f"  {min(i + BATCH_SIZE, len(missing))}/{len(missing)} processed ...")

        print(f"\nDone. Generated info for {n_done} skills.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
