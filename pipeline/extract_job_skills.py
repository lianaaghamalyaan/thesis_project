"""
Incremental LLM skill extraction for job postings that are missing from
data/processed/unified/job_skills_by_id.json.

Context: the historical extraction (whichever notebook/script produced the
original job_skills_norm.json — not present in this repo) covered 650 of the
753 current postings. The other 103 are from sources added later
(betconstruct, nvidia, superannotate, teamviewer, griddynamics, plus more
epam postings) and have never been through skill extraction. This script
fills that gap and is safe to re-run on every future scrape (idempotent —
only processes job_ids not already present).

Requires ANTHROPIC_API_KEY in the environment. Does not exist in this repo's
dev environment as of 2026-07-10, so this script is written but not yet run.

Note on methodology: this is a new prompt, not a byte-for-byt reproduction of
whatever produced the original 650 extractions (that prompt isn't in the
repo). Output is normalized through the existing skill_normalization_map.json
so results land in the same vocabulary as historical data. Track the prompt
used via PROMPT_VERSION below for reproducibility, per
docs/product/data_pipeline_architecture.md's versioning principles.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python pipeline/extract_job_skills.py [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS_CSV = ROOT / "data/processed/jobs/final_jobs_dataset_it_only.csv"
SKILLS_JSON = ROOT / "data/processed/unified/job_skills_by_id.json"
NORM_MAP_JSON = ROOT / "data/processed/unified/skill_normalization_map.json"

PROMPT_VERSION = "job_skills_v1_2026-07-10"
MODEL = "claude-haiku-4-5-20251001"

EXTRACTION_PROMPT = """You are extracting a flat list of skills, technologies, tools, and \
languages mentioned or clearly implied in this IT job posting. Match the style of: \
specific technology names (e.g. "React", "Kubernetes"), tools, programming languages, \
spoken languages required, and named methodologies (e.g. "Agile"). Do not include \
generic soft-skill phrases ("team player"), company names, or job titles.

Return ONLY a JSON array of strings, nothing else. Example: \
["Python", "Django", "PostgreSQL", "English", "Docker"]

Job posting:
Title: {title}
Company: {company}
Text: {text}"""


def load_normalization_map() -> dict:
    with open(NORM_MAP_JSON) as f:
        return json.load(f)


def normalize_skills(raw_skills: list[str], norm_map: dict) -> list[str]:
    seen = set()
    out = []
    for s in raw_skills:
        canonical = norm_map.get(s, s)
        if canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
    return out


def extract_one(client, title: str, company: str, text: str) -> list[str]:
    prompt = EXTRACTION_PROMPT.format(title=title, company=company, text=(text or "")[:6000])
    resp = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = resp.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").lstrip("json").strip()
    try:
        skills = json.loads(raw_text)
    except json.JSONDecodeError:
        print(f"  WARNING: could not parse model output, skipping. Raw: {raw_text[:200]}", file=sys.stderr)
        return []
    return [s for s in skills if isinstance(s, str)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without calling the API")
    parser.add_argument("--limit", type=int, default=None, help="Process at most N postings (for testing)")
    args = parser.parse_args()

    import pandas as pd

    df = pd.read_csv(JOBS_CSV)
    if "job_id" not in df.columns:
        print("ERROR: jobs CSV has no job_id column. Run pipeline/migrations/001_stable_job_id.py first.", file=sys.stderr)
        sys.exit(1)

    with open(SKILLS_JSON) as f:
        existing = json.load(f)

    missing = df[~df["job_id"].isin(existing.keys())]
    if args.limit:
        missing = missing.head(args.limit)

    print(f"{len(missing)} of {len(df)} postings need extraction (prompt_version={PROMPT_VERSION}, model={MODEL}).")

    if args.dry_run:
        print("Dry run — not calling the API. Sample of postings that would be processed:")
        print(missing[["job_id", "source", "job_title", "company_name"]].head(10).to_string(index=False))
        return

    if missing.empty:
        print("Nothing to do.")
        return

    import anthropic
    client = anthropic.Anthropic()
    norm_map = load_normalization_map()

    for _, row in missing.iterrows():
        try:
            raw_skills = extract_one(client, row["job_title"], row["company_name"], row["full_text"])
        except Exception as e:
            print(f"  ERROR extracting {row['job_id']} ({row['job_title']}): {e}", file=sys.stderr)
            continue
        existing[row["job_id"]] = normalize_skills(raw_skills, norm_map)
        print(f"  {row['job_id']}  {row['job_title'][:50]:<50}  {len(raw_skills)} skills")
        time.sleep(0.2)  # gentle on rate limits

    with open(SKILLS_JSON, "w") as f:
        json.dump(existing, f, indent=1, ensure_ascii=False)
    print(f"Wrote {SKILLS_JSON} — {len(existing)} of {len(df)} postings now covered.")


if __name__ == "__main__":
    main()
