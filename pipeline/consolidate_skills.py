"""Permanent pipeline step: merge job_skills near-duplicate names into an
already-existing course_skills canonical name.

Why this exists: every skill-extraction run (weekly scraping included)
reintroduces spelling/acronym/wording variants of skills the curriculum
already teaches — "NLP" vs "Natural Language Processing", "Apache Airflow"
vs "Airflow", "REST APIs" vs "APIs". Left unmerged, each variant is a
separate skill_name row: the "core skill" denominator inflates with
duplicates of the same real-world skill, and a program that teaches the
skill under one wording shows up with a false gap under the other. This was
found and manually fixed once (2026-07-18/19, see git history around that
date) using exactly this logic in one-off scratch scripts; this module is
that logic turned into a permanent, idempotent, re-runnable step so the
same problem doesn't quietly reappear after every future scrape.

Two independent detection passes, both deliberately biased toward
PRECISION over recall — a missed merge just leaves two near-duplicate
skills diluting scores a little (self-correcting once caught), but a false
merge silently conflates two different skills, which is much harder to
notice after the fact and actively wrong. This choice was empirically
tested: lowering the semantic pass's threshold from 0.78 to 0.65 nearly
tripled the candidate count but introduced real false positives at an
observed ~2-3% rate (e.g. "Design Systems" -> "Information Systems Design",
"VACUUM" -> "Vacuum Electronics", "quality monitoring" -> "Water Quality
Monitoring" — coincidental embedding similarity between unrelated
domains). 0.78 did not exhibit this in manual review and is the default.

Pass 1 (semantic + word-subset): a job-only skill name merges into an
existing course_skills name if they clear SEMANTIC_THRESHOLD cosine
similarity AND either (a) one phrase's words are a subset of the other's
(e.g. "Airflow" subset of "Apache Airflow"), or (b) they're acronym/plural
variants of each other by initials. Guards: the shorter phrase must be
multi-word or a real acronym (drops single-generic-word merges like
"Design" -> "Game Design"); phrases with mismatched digit sequences never
merge (drops "ISO 42001" -> "ISO 27001" — different standards, not a name
variant); phrases with a negation flip never merge (drops "No-SQL" ->
"SQL" — opposite meaning).

Pass 2 (parenthetical acronym pairs): the vocabulary's own "X (Y)" or
"Y (X)" entries (e.g. "NLP (Natural Language Processing)") are trusted
ground truth for what an acronym means IN THIS DATASET — no embedding
needed. This exists because sentence embeddings do NOT reliably see a bare
acronym as similar to its own expansion (cosine "LLMs" vs "Large Language
Models" = 0.14 despite being the literal same concept), so pass 1 misses
these even though they're the highest-confidence merges available. Guard:
the acronym's letters must actually equal the initials of the expansion's
words, or a garbled extraction like "Streaming (LLM)" (not a real acronym
pair) gets accepted as "LLM means Streaming".

A small curated list (CURATED_SUBSTRING_PAIRS) covers manually-reviewed
word-subset pairs whose embedding similarity falls just under the pass-1
threshold (0.59-0.77) despite being genuine — Airflow/CI-CD/REST-API
variants. Kept short and explicit rather than lowering the general
threshold, per the precision-over-recall rationale above.

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.consolidate_skills [--dry-run] [--threshold 0.78]

Run this after importing/extracting new job postings' skills and BEFORE
pipeline/build_skill_embeddings.py + pipeline/compute_alignment.py, as part
of the normal refresh sequence — a fresh scrape's skill extraction always
needs this pass before the alignment numbers it produces can be trusted.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SEMANTIC_THRESHOLD = 0.78
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Manually reviewed 2026-07-19/20: genuine word-subset pairs whose cosine
# similarity (0.59-0.77) falls under SEMANTIC_THRESHOLD. (shorter, longer) —
# shorter becomes the merge target unless the longer form is the one that
# actually exists in course_skills.
CURATED_SUBSTRING_PAIRS: list[tuple[str, str]] = [
    ("Airflow", "Apache Airflow"),
    ("APIs", "REST APIs"),
    ("CI/CD", "CI/CD pipelines"),
    ("CI/CD", "GitLab CI/CD"),
]

# Manually reviewed 2026-07-19: word-subset pairs that clear
# SEMANTIC_THRESHOLD but are false merges — the longer form adds a domain
# qualifier the shorter, generic source doesn't imply (a job posting saying
# "Analytical Methods" is not necessarily about chemistry). Word-subset
# containment alone can't distinguish "genuine wording variant" from "this
# happens to be a narrower specialization" — these three are the only
# instances observed in production so far; add here if more turn up rather
# than loosening the general guards.
MANUAL_EXCLUDE_SOURCES: set[str] = {
    "Analytical Methods",     # not "Chemical Analytical Methods"
    "Data Workflows",         # not "Financial Data Workflows"
    "Product Analytics",      # not "New Product Development Analytics"
}

NEGATORS = {"no", "non", "un", "not", "anti", "without"}


def _word_set(phrase: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9/+#.]+", phrase.lower()))


def _word_count(phrase: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", phrase))


def _initials(phrase: str) -> str:
    return "".join(w[0] for w in re.findall(r"[A-Za-z]+", phrase)).upper()


def _is_acronym(phrase: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", phrase)
    return 2 <= len(letters) <= 6 and letters.isupper()


def _has_negation_flip(a: str, b: str) -> bool:
    def negated(words: set[str]) -> bool:
        return any(w.rstrip("-") in NEGATORS or w.startswith(("non-", "non", "un-", "anti-")) for w in words)
    return negated(_word_set(a)) != negated(_word_set(b))


def _has_digit_mismatch(a: str, b: str) -> bool:
    da, db = set(re.findall(r"\d{2,}", a)), set(re.findall(r"\d{2,}", b))
    return bool(da) and bool(db) and da.isdisjoint(db)


def build_semantic_merge_map(
    course_canon: list[str], job_only: list[str], model, threshold: float = SEMANTIC_THRESHOLD
) -> dict[str, tuple[str, float]]:
    """Pass 1: semantic + word-subset/acronym-plural merges. One best
    (highest-similarity) target per source skill."""
    import numpy as np

    course_embs = np.array(model.encode(course_canon, batch_size=256, show_progress_bar=False, normalize_embeddings=True))
    job_embs = np.array(model.encode(job_only, batch_size=256, show_progress_bar=False, normalize_embeddings=True))
    course_words = {c: _word_set(c) for c in course_canon}

    merge_map: dict[str, tuple[str, float]] = {}
    for j, jemb in zip(job_only, job_embs):
        jw = _word_set(j)
        j_clean = re.sub(r"[^A-Za-z]", "", j)
        j_init = _initials(j)
        sims = course_embs @ jemb
        best_c, best_sim = None, -1.0
        for idx, c in enumerate(course_canon):
            sim = float(sims[idx])
            if sim < threshold:
                continue
            cw = course_words[c]
            shorter, longer = (jw, cw) if len(jw) <= len(cw) else (cw, jw)
            word_subset = bool(shorter) and shorter.issubset(longer) and shorter != longer
            acro_match = (
                (j_clean.isupper() and j_clean == re.sub(r"[^A-Za-z]", "", c))
                or (j_clean.endswith("s") and j_clean[:-1].isupper() and j_clean[:-1] == re.sub(r"[^A-Za-z]", "", c))
                or (_is_acronym(j) and _initials(c) == j_clean)
                or (_is_acronym(c) and j_init == re.sub(r"[^A-Za-z]", "", c))
            )
            if not (word_subset or acro_match):
                continue
            shorter_phrase = j if _word_count(j) <= _word_count(c) else c
            if _word_count(shorter_phrase) < 2 and not _is_acronym(shorter_phrase):
                continue
            if _has_negation_flip(j, c) or _has_digit_mismatch(j, c):
                continue
            if sim > best_sim:
                best_c, best_sim = c, sim
        if best_c is not None:
            merge_map[j] = (best_c, best_sim)
    return merge_map


def build_acronym_merge_map(course_canon: list[str], job_canon: list[str]) -> dict[str, str]:
    """Pass 2: acronym<->expansion pairs extracted from the vocabulary's own
    "X (Y)" entries, validated against the expansion's real initials."""
    course_set = set(course_canon)
    all_vocab = set(course_canon) | set(job_canon)

    pat1 = re.compile(r"^([A-Za-z0-9/&+#.\- ]{2,8})\s*\(([A-Za-z][A-Za-z0-9/&+#.\- ]{4,60})\)$")
    pat2 = re.compile(r"^([A-Za-z][A-Za-z0-9/&+#.\- ]{4,60})\s*\(([A-Za-z0-9/&+#.\- ]{2,8})\)$")

    acro_pairs: dict[str, str] = {}
    for name in all_vocab:
        acro = expansion = None
        m = pat1.match(name.strip())
        if m and re.sub(r"[^A-Za-z]", "", m.group(1)).isupper():
            acro, expansion = m.group(1).strip(), m.group(2).strip()
        else:
            m = pat2.match(name.strip())
            if m and re.sub(r"[^A-Za-z]", "", m.group(2)).isupper():
                expansion, acro = m.group(1).strip(), m.group(2).strip()
        if acro is None:
            continue
        acro_letters = re.sub(r"[^A-Za-z]", "", acro).upper()
        exp_initials = _initials(expansion)
        if not (exp_initials == acro_letters or exp_initials.startswith(acro_letters) or acro_letters.startswith(exp_initials)):
            continue
        acro_pairs[acro] = expansion

    merge_map: dict[str, str] = {}
    for acro, expansion in acro_pairs.items():
        if expansion not in course_set and expansion not in job_canon:
            continue
        for variant in {acro, acro + "s", acro.upper(), acro.upper() + "s"}:
            if variant in job_canon and variant != expansion:
                merge_map[variant] = expansion
    return merge_map


def build_curated_merge_map(course_canon: list[str], job_canon: list[str]) -> dict[str, str]:
    course_set = set(course_canon)
    merge_map: dict[str, str] = {}
    for shorter, longer in CURATED_SUBSTRING_PAIRS:
        if shorter not in job_canon or longer not in job_canon or shorter == longer:
            continue
        target = longer if (shorter not in course_set and longer in course_set) else shorter
        source = longer if target == shorter else shorter
        merge_map[source] = target
    return merge_map


def build_merge_map(course_canon: list[str], job_canon: list[str], model, threshold: float = SEMANTIC_THRESHOLD) -> dict[str, str]:
    course_set = set(course_canon)
    job_only = [s for s in job_canon if s not in course_set]

    semantic = {src: target for src, (target, _sim) in build_semantic_merge_map(course_canon, job_only, model, threshold).items()}
    acronym = build_acronym_merge_map(course_canon, job_canon)
    curated = build_curated_merge_map(course_canon, job_canon)

    # Later passes don't override an already-decided merge for the same source.
    merge_map: dict[str, str] = dict(semantic)
    for src, target in {**acronym, **curated}.items():
        merge_map.setdefault(src, target)
    for src in MANUAL_EXCLUDE_SOURCES:
        merge_map.pop(src, None)
    return merge_map


def apply_merge_map(session, merge_map: dict[str, str], dry_run: bool) -> None:
    from sqlalchemy import text

    rows = session.execute(text("SELECT id, posting_id, skill_name FROM job_skills")).all()
    by_posting: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for row_id, posting_id, skill_name in rows:
        by_posting[posting_id].append((row_id, skill_name))

    affected_postings = {
        pid for pid, entries in by_posting.items()
        if any(name in merge_map for _, name in entries)
    }
    print(f"{len(affected_postings)} postings affected out of {len(by_posting)} total.")

    to_delete_ids: list[int] = []
    to_insert: list[tuple[int, str, str, str]] = []
    n_deduped = 0
    for pid in affected_postings:
        entries = by_posting[pid]
        old_ids = [row_id for row_id, _ in entries]
        new_names = {merge_map.get(name, name) for _, name in entries}
        n_deduped += len(entries) - len(new_names)
        to_delete_ids.extend(old_ids)
        to_insert.extend((pid, name, "LLM", "consolidate_skills") for name in new_names)

    print(f"Rows before: {len(to_delete_ids)}, rows after: {len(to_insert)} "
          f"({n_deduped} collapsed as true duplicates within a posting).")

    if dry_run or not to_delete_ids:
        print("Dry run — no writes." if dry_run else "Nothing to merge.")
        return

    from psycopg2.extras import execute_values

    raw_conn = session.connection().connection
    with raw_conn.cursor() as cur:
        cur.execute("DELETE FROM job_skills WHERE id = ANY(%s)", (to_delete_ids,))
        execute_values(
            cur,
            "INSERT INTO job_skills (posting_id, skill_name, extraction_method, prompt_version) VALUES %s",
            to_insert,
        )
    session.commit()
    total_distinct = session.execute(text("SELECT COUNT(DISTINCT skill_name) FROM job_skills")).scalar_one()
    print(f"Done. job_skills now has {total_distinct} distinct skill names.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--threshold", type=float, default=SEMANTIC_THRESHOLD)
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer
    from sqlalchemy import text

    from server.db import get_session

    session = get_session()
    try:
        course_canon = sorted({r[0] for r in session.execute(text("SELECT DISTINCT skill_name FROM course_skills")).all()})
        job_canon = sorted({r[0] for r in session.execute(text("SELECT DISTINCT skill_name FROM job_skills")).all()})
        print(f"{len(course_canon)} distinct course_skills, {len(job_canon)} distinct job_skills.")

        model = SentenceTransformer(EMBEDDING_MODEL)
        merge_map = build_merge_map(course_canon, job_canon, model, args.threshold)

        print(f"\n{len(merge_map)} merge pairs found:")
        for src, target in sorted(merge_map.items()):
            print(f"  {src!r:45s} -> {target!r}")

        if not merge_map:
            print("\nNothing to consolidate — vocabulary is already clean.")
            return

        print()
        apply_merge_map(session, merge_map, args.dry_run)
    finally:
        session.close()


if __name__ == "__main__":
    main()
