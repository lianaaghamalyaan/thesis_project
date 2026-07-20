"""Extract skills for active IT postings that have zero job_skills rows —
i.e. postings pipeline/import_new_postings.py just inserted this run, or any
older posting that's somehow never been through extraction. Writes directly
to job_skills (not a separate audit table): this is deliberately simpler
than pipeline/reextract_job_skills_v2.py, which built a fully auditable,
resumable, reviewable re-extraction pipeline for a ONE-TIME historical
re-extraction of 1,102 postings at once under close human review. A weekly
increment is a much smaller batch (tens of postings, not thousands), and the
two permanent safety nets this repo now has —
pipeline/consolidate_skills.py (merges near-duplicate names) and
pipeline/verify_promotion_gate.py (blocks promotion on implausible score
movement) — cover what the audit-table ceremony was protecting against, so
it isn't worth re-imposing on every automated run.

Reuses the exact same evidence-based prompt as reextract_job_skills_v2.py
(imported from there, not copy-pasted) so postings extracted incrementally
here land in the same style/quality as the July 2026 historical batch.

Requires ANTHROPIC_API_KEY in the environment.

Usage:
    DATABASE_URL=... ANTHROPIC_API_KEY=... ./.venv_dashboard/bin/python -m pipeline.extract_new_postings_skills [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    from sqlalchemy import select

    from pipeline.extract_course_skills import normalize_skills
    from pipeline.reextract_job_skills_v2 import (
        MODEL,
        PROMPT_VERSION,
        message_text,
        parse_response,
        text_chunks,
    )
    from server.db import SessionLocal
    from server.models import JobPosting, JobSkill

    session = SessionLocal()
    try:
        postings = session.execute(
            select(JobPosting)
            .outerjoin(JobSkill, JobSkill.posting_id == JobPosting.id)
            .where(
                JobPosting.is_active == True,  # noqa: E712
                JobPosting.is_it_job == True,  # noqa: E712
                JobSkill.id.is_(None),
            )
        ).scalars().all()

        if args.limit:
            postings = postings[: args.limit]

        print(f"{len(postings)} active IT postings with zero job_skills rows.")
        if not postings:
            return

        if args.dry_run:
            print("Dry run — no extraction, no writes. Sample:")
            for p in postings[:10]:
                print(f"  {p.job_id}  {p.title!r}  ({p.it_role_group})")
            return

        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set. Required for skill extraction.")

        import anthropic
        client = anthropic.Anthropic()

        from pipeline.reextract_job_skills_v2 import SYSTEM_PROMPT

        n_extracted = 0
        n_failed = 0
        for i, posting in enumerate(postings, start=1):
            skills_seen: dict[str, str] = {}  # skill -> evidence, deduped within this posting
            try:
                for chunk_index, chunk in enumerate(text_chunks(posting.full_text or ""), start=1):
                    prompt = (
                        f"Title: {posting.title}\n"
                        f"Company: {posting.company_name or ''}\n"
                        f"Role group: {posting.it_role_group or ''}\n"
                        f"Excerpt {chunk_index}:\n{chunk}"
                    )
                    response = client.messages.create(
                        model=MODEL, max_tokens=3000, system=SYSTEM_PROMPT,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    for record in parse_response(message_text(response)):
                        skills_seen[record["skill"]] = record["evidence"]
            except Exception as e:  # noqa: BLE001 - one bad posting shouldn't kill the whole batch
                print(f"  [{i}/{len(postings)}] FAILED on {posting.job_id}: {e}", file=sys.stderr)
                n_failed += 1
                continue

            # Fold each raw phrase into the nearest existing canonical skill
            # name (cosine >= 0.85), exactly as pipeline/add_july_postings.py
            # did — so a freshly-scraped "NodeJS"/"Node.js" spelling variant
            # joins the existing vocabulary instead of adding a near-duplicate.
            # Without this, weekly automation would slowly re-fragment the
            # vocabulary that pipeline/consolidate_skills.py (which only
            # catches acronym/word-subset pairs, a narrower net) can't fully
            # reunify. dedupe after mapping: two raw phrases can normalize to
            # the same canonical name.
            canonical = set(normalize_skills(list(skills_seen), session))
            for skill_name in canonical:
                session.add(JobSkill(
                    posting_id=posting.id, skill_name=skill_name,
                    extraction_method="LLM", prompt_version=PROMPT_VERSION,
                ))
            n_extracted += 1
            if i % 20 == 0:
                session.commit()
                print(f"  [{i}/{len(postings)}] extracted so far, committing ...")

        session.commit()
        print(f"\nDone. Extracted skills for {n_extracted} postings ({n_failed} failed — rerun this script to "
              "retry just those, since it only ever targets postings with zero job_skills rows).")
        print("Next: pipeline.consolidate_skills, pipeline.build_skill_embeddings, pipeline.compute_alignment.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
