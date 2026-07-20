"""Live alignment computation pipeline.

Reconstructs the frozen March 2026 snapshot's methodology exactly, as
recovered from the original pipeline notebook (deleted from the current
tree but recovered from git history: a7e54d8's
notebooks/03_pipeline/01_run_alignment.ipynb) and cross-checked against
thesis/thesis_final.docx §1.6 (paras 143, 146-149, 157-161, 260, 265):

  - Semantic matching: cosine similarity >= 0.65 (sentence-transformers),
    bidirectional (job-skill -> nearest program-skill AND vice versa),
    with a hardcoded BLOCKLIST (semantically-close but functionally
    distinct pairs, e.g. React/Angular) and ALLOWLIST (pairs that should
    count as covered even below threshold, e.g. Python -> NumPy/Pandas)
    overriding the raw cosine decision. Coverage is measured as the
    fraction of *job* skills matched by some program skill.
  - Skill vocabulary consolidation happens upstream, not in this script:
    server/fix_job_skills.py and server/fix_course_skills.py populate
    course_skills / job_skills from data/processed/unified/
    course_skills_with_desc_norm.json and job_skills_norm.json, both of
    which already went through the original 0.85-cosine clustering pass
    (see fix_job_skills.py's docstring). This script assumes DB skill
    names are already consolidated concepts, not raw phrases.
  - full_coverage_pct: |program skills ∩ ALL market skills| / |ALL market
    skills| x 100.
  - core_role_coverage_pct ("core skill" definition, thesis para 161): for
    a program's relevant role(s), a market skill counts as "core" if it
    appears in at least 5% of that *role's own* postings. For programs
    mapped to multiple roles, the core sets from each role are UNIONED
    (not averaged per-role) and ONE coverage number is computed against
    that union — this matches the original notebook's
    get_core_job_skills() exactly, not the "score per role then average"
    reading that an earlier version of this script used and which failed
    to reproduce the thesis's published numbers.
  - weighted_core_coverage_pct: same core union, each skill's contribution
    weighted by its combined (summed across relevant roles) posting
    frequency rather than counted equally — the thesis's primary reported
    metric ("the main measure employed throughout the thesis").
  - Programs with relevant_roles == NULL in the database (thesis para 459:
    4 programs, e.g. "Blockchain and Digital Currencies", genuinely
    unmapped to any IT role group) get full_coverage_pct only — no
    role/core/weighted score at all. This is distinct from
    relevant_roles == "ALL" (general programs deliberately compared
    against the whole market), which synthesizes a single all-postings
    "role" and scores normally against it. An earlier version of this
    script conflated the two, which is why Blockchain and Digital
    Currencies incorrectly showed a role-aware score in a prior dry run.

Validation: --validate-650 restricts the postings pool to the original
650 (data/processed/jobs/_recovered_final_jobs_dataset_it_with_roles.csv,
recovered from git history) and their historical 9-category role
taxonomy. This exactly reproduces the thesis's published YSU "Data
Science in Business" numbers (core=62.5%, weighted=75.46%) — confirmed
empirically 2026-07-12 after fixing the job-skill consolidation bug (see
fix_job_skills.py) and the row-misalignment bug (job_skills_norm.json is
indexed against a since-regenerated jobs CSV; the recovered file restores
the original row order/role labels it was built against).

Usage:
    DATABASE_URL=... ./.venv_dashboard/bin/python -m pipeline.compute_alignment [--university NAME] [--dry-run] [--validate-650]

Requires sentence-transformers (pipeline/requirements.txt).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SIMILARITY_THRESHOLD = 0.65  # thesis_final.docx para 260: calibrated value
CORE_SKILL_FREQ_PCT = 0.05   # thesis_final.docx para 161: "at least 5% of such posts"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RUN_KEY_PREFIX = "live"
# Fallback only, used if a run somehow has zero active postings with a known
# posting_date (job_snapshot_date is otherwise derived live below from
# MAX(posting_date) among postings actually in scope, so it self-updates on
# every recompute instead of needing a human to remember to bump a
# hardcoded constant — see server/seed.py's JOB_SNAPSHOT_DATE for the
# separate one-time-seed constant, which is a different code path).
JOB_SNAPSHOT_DATE_FALLBACK = date(2026, 3, 20)
RECOVERED_650_PATH = ROOT / "data" / "processed" / "jobs" / "_recovered_final_jobs_dataset_it_with_roles.csv"

BLOCKLIST = {
    ('Graph Databases', 'GraphQL'), ('GraphQL', 'Graph Databases'),
    ('Diffusion Models', 'Stable Diffusion'), ('Stable Diffusion', 'Diffusion Models'),
    ('Classical Mechanics', 'Machine Learning'), ('Game Theory', 'Game Development'),
    ('React', 'Angular'), ('Angular', 'React'),
    ('React', 'Vue.js'), ('Vue.js', 'React'),
    ('Angular', 'Vue.js'), ('Vue.js', 'Angular'),
    ('Spring Framework', 'Django'), ('Django', 'Spring Framework'),
    ('Spring Framework', 'Flask'), ('Flask', 'Spring Framework'),
    ('TypeScript', 'JavaScript'), ('JavaScript', 'TypeScript'),
    ('Docker', 'Kubernetes'), ('Kubernetes', 'Docker'),
}
ALLOWLIST = {
    ('Relational Databases', 'SQL'), ('Relational Databases', 'PostgreSQL'),
    ('Relational Databases', 'MySQL'), ('Database Management', 'SQL'),
    ('Database Management', 'PostgreSQL'), ('Database Management', 'MySQL'),
    ('Database Management', 'MongoDB'), ('Version Control', 'Git'),
    ('Version Control Systems', 'Git'), ('Cloud Computing', 'AWS'),
    ('Cloud Computing', 'Azure'), ('Cloud Computing', 'Google Cloud Platform'),
    ('Software Testing', 'Unit Testing'), ('Software Testing', 'Test Automation'),
    ('Web Development', 'HTML'), ('Web Development', 'CSS'),
    ('Network Security', 'Firewalls'), ('Network Security', 'Intrusion Detection'),
    ('Database Normalization', 'SQL'),
    ('Python', 'NumPy'), ('Python', 'Pandas'),
    ('Java', 'Spring Framework'),
    ('C++', 'Memory Management'),
    ('PostgreSQL', 'SQL'),
}


def compute_alignment(university: str | None = None, dry_run: bool = False, validate_650: bool = False) -> str | None:
    """Computes a fresh AlignmentRun for the given university (or all
    universities if None). Returns the new run_key, or None if dry_run."""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import pandas as pd
    from sqlalchemy import func, select

    from server.db import get_session
    from server.models import (
        AlignmentResult,
        AlignmentRun,
        Course,
        CourseSkill,
        GapSkill,
        JobPosting,
        JobSkill,
        Program,
        ProgramVersion,
        University,
    )
    # programs.relevant_roles uses the original 9-category taxonomy (thesis
    # para 146) while job_postings.it_role_group uses a newer 13-category
    # scraper classification. expand_program_roles() lives in
    # server/role_mapping.py — shared with server/analytics.py so the
    # headline coverage score and the Strengths/Gaps computed for the same
    # program can't silently diverge onto different job-market slices (see
    # that module's docstring for the history of why this was split out).
    from server.role_mapping import expand_program_roles

    session = get_session()
    try:
        # ── Load current-version course skills, grouped by program ──────
        q = (
            select(Program.id, Program.name, Program.degree_level, Program.relevant_roles,
                   University.name, CourseSkill.skill_name)
            .select_from(CourseSkill)
            .join(Course, CourseSkill.course_id == Course.id)
            .join(ProgramVersion, Course.program_version_id == ProgramVersion.id)
            .join(Program, ProgramVersion.program_id == Program.id)
            .join(University, Program.university_id == University.id)
            .where(ProgramVersion.is_current == True)  # noqa: E712
        )
        if university:
            q = q.where(University.name == university)
        rows = session.execute(q).all()

        program_meta: dict[int, dict] = {}
        program_skills: dict[int, set[str]] = {}
        for program_id, name, degree, relevant_roles, uni_name, skill in rows:
            program_meta[program_id] = {
                "name": name, "degree": degree, "relevant_roles": relevant_roles, "university": uni_name,
            }
            program_skills.setdefault(program_id, set()).add(skill)

        if not program_skills:
            print("No programs with course skills found for the given scope.")
            return None

        # ── Load active job postings (all of them, independent of the skill
        # join below) so n_active_postings and job_snapshot_date reflect the
        # true active-postings pool — a posting with zero extracted skills
        # still counts as "active data in scope" and still has a real
        # posting_date, but would silently disappear from both if derived
        # from the skills join instead (that undercounted n_active_postings
        # by however many postings had no extracted skills, and there was
        # no live date signal at all — job_snapshot_date was a hardcoded
        # constant a human had to remember to bump after every scrape). ──
        active_postings = session.execute(
            select(JobPosting.id, JobPosting.source_url, JobPosting.posting_date)
            .where(JobPosting.is_active == True)  # noqa: E712
        ).all()

        # ── Load active job postings' skills + role group ────────────────
        if validate_650:
            recovered = pd.read_csv(RECOVERED_650_PATH)
            valid_urls = set(recovered["source_url"])
            url_to_role = dict(zip(recovered["source_url"], recovered["role_group"]))
            print(f"--validate-650: restricting to the original {len(recovered)} postings "
                  f"(original 9-category role taxonomy).")

            active_postings = [(pid, url, d) for pid, url, d in active_postings if url in valid_urls]

            jq = (
                select(JobPosting.id, JobPosting.source_url, JobSkill.skill_name)
                .join(JobSkill, JobSkill.posting_id == JobPosting.id)
                .where(JobPosting.is_active == True)  # noqa: E712
            )
            jrows = session.execute(jq).all()

            posting_skills: dict[int, set[str]] = {}
            posting_role: dict[int, str | None] = {}
            for posting_id, source_url, skill in jrows:
                if source_url not in valid_urls:
                    continue
                posting_skills.setdefault(posting_id, set()).add(skill)
                posting_role[posting_id] = url_to_role.get(source_url)
        else:
            jq = (
                select(JobPosting.id, JobPosting.it_role_group, JobSkill.skill_name)
                .join(JobSkill, JobSkill.posting_id == JobPosting.id)
                .where(JobPosting.is_active == True)  # noqa: E712
            )
            jrows = session.execute(jq).all()

            posting_skills = {}
            posting_role = {}
            for posting_id, role, skill in jrows:
                posting_skills.setdefault(posting_id, set()).add(skill)
                posting_role[posting_id] = role

        n_active_postings_total = len(active_postings)
        active_dates = [d for _, _, d in active_postings if d is not None]
        max_posting_date = max(active_dates) if active_dates else None
        n_unknown_posting_date = n_active_postings_total - len(active_dates)

        role_posting_count: Counter = Counter()
        role_skill_doc_freq: dict[str, Counter] = {}
        all_market_skills: set[str] = set()
        for posting_id, skills in posting_skills.items():
            role = posting_role.get(posting_id)
            if role:
                role_posting_count[role] += 1
            all_market_skills.update(skills)
            for skill in skills:
                if role:
                    role_skill_doc_freq.setdefault(role, Counter())[skill] += 1

        known_job_roles = set(role_skill_doc_freq.keys())
        print(f"{len(program_skills)} programs, {len(all_market_skills)} distinct market skills, "
              f"{len(posting_skills)} postings with extracted skills "
              f"({n_active_postings_total} active postings total, "
              f"{n_active_postings_total - len(posting_skills)} with none), "
              f"{len(known_job_roles)} role groups.")

        # ── Embed every distinct skill phrase once (courses + jobs) ──────
        all_course_skills = set().union(*program_skills.values()) if program_skills else set()
        vocab = sorted(all_course_skills | all_market_skills)
        print(f"Embedding {len(vocab)} distinct skill phrases with {EMBEDDING_MODEL} ...")
        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(vocab, show_progress_bar=False, normalize_embeddings=True)
        skill_to_emb = {s: embeddings[i] for i, s in enumerate(vocab)}

        def compute_semantic_alignment(prog_skills: set[str], job_skills: set[str]) -> dict:
            """Bidirectional threshold matching with blocklist/allowlist
            overrides, exactly matching the original notebook. Coverage is
            the fraction of job_skills matched by some program skill."""
            prog_list = [s for s in prog_skills if s in skill_to_emb]
            job_list = [s for s in job_skills if s in skill_to_emb]
            if not prog_list or not job_list:
                return {"n_overlap": 0, "coverage_pct": 0.0, "n_job_skills": len(job_list), "overlap_skills": [], "gap_skills": sorted(job_list)}

            prog_m = np.array([skill_to_emb[s] for s in prog_list])
            job_m = np.array([skill_to_emb[s] for s in job_list])
            sims = job_m @ prog_m.T

            job_covered = np.zeros(len(job_list), dtype=bool)
            for j in range(len(job_list)):
                max_sim = sims[j].max()
                best_prog = prog_list[int(sims[j].argmax())]
                if (best_prog, job_list[j]) in BLOCKLIST:
                    for pi in sims[j].argsort()[::-1]:
                        if sims[j][pi] < SIMILARITY_THRESHOLD:
                            break
                        if (prog_list[pi], job_list[j]) not in BLOCKLIST:
                            job_covered[j] = True
                            break
                elif max_sim >= SIMILARITY_THRESHOLD:
                    job_covered[j] = True
                else:
                    for pi in range(len(prog_list)):
                        if (prog_list[pi], job_list[j]) in ALLOWLIST:
                            job_covered[j] = True
                            break

            overlap_skills = [job_list[j] for j in range(len(job_list)) if job_covered[j]]
            gap_skills = [job_list[j] for j in range(len(job_list)) if not job_covered[j]]
            return {
                "n_overlap": int(job_covered.sum()),
                "coverage_pct": round(float(job_covered.mean()) * 100, 2),
                "n_job_skills": len(job_list),
                "overlap_skills": overlap_skills,
                "gap_skills": gap_skills,
            }

        def get_core_job_skills(relevant_roles: set[str]) -> set[str]:
            out: set[str] = set()
            for rg in relevant_roles:
                n_rg = role_posting_count.get(rg, 0)
                if n_rg == 0:
                    continue
                min_count = max(1, round(CORE_SKILL_FREQ_PCT * n_rg))
                out |= {s for s, c in role_skill_doc_freq[rg].items() if c >= min_count}
            return out

        def get_freq_map(relevant_roles: set[str]) -> Counter:
            combined: Counter = Counter()
            for rg in relevant_roles:
                for s, c in role_skill_doc_freq.get(rg, {}).items():
                    combined[s] += c
            return combined

        def compute_weighted_coverage(overlap_skills: list[str], job_skills: set[str], freq_map: Counter) -> float | None:
            if not job_skills or not freq_map:
                return None
            total_weight = sum(freq_map.get(s, 0) for s in job_skills)
            if total_weight == 0:
                return None
            overlap_weight = sum(freq_map.get(s, 0) for s in overlap_skills if s in job_skills)
            return round(overlap_weight / total_weight * 100, 2)

        # ── Per-program metrics ──────────────────────────────────────────
        results = []
        for program_id, skills in program_skills.items():
            meta = program_meta[program_id]
            raw_roles = meta["relevant_roles"]

            full = compute_semantic_alignment(skills, all_market_skills)

            role_coverage_pct = core_role_coverage_pct = weighted_core_coverage_pct = None
            core_n_job_skills = core_n_overlap = None
            gap_skills_sorted: list[tuple[str, int]] = []

            if raw_roles is None:
                # thesis para 459: genuinely unmapped — full coverage only.
                pass
            else:
                role_set = expand_program_roles(raw_roles, known_job_roles)

                if role_set:
                    role_job_skills: set[str] = set()
                    for rg in role_set:
                        role_job_skills |= set(role_skill_doc_freq.get(rg, {}).keys())
                    role = compute_semantic_alignment(skills, role_job_skills)
                    role_coverage_pct = role["coverage_pct"]

                    core_job_skills_set = get_core_job_skills(role_set)
                    if core_job_skills_set:
                        core = compute_semantic_alignment(skills, core_job_skills_set)
                        core_role_coverage_pct = core["coverage_pct"]
                        core_n_job_skills = core["n_job_skills"]
                        core_n_overlap = core["n_overlap"]

                        freq_map = get_freq_map(role_set)
                        weighted_core_coverage_pct = compute_weighted_coverage(
                            core["overlap_skills"], core_job_skills_set, freq_map
                        )

                        gap_freqs = {s: freq_map.get(s, 0) for s in core["gap_skills"]}
                        gap_skills_sorted = sorted(gap_freqs.items(), key=lambda kv: -kv[1])

            results.append({
                "program_id": program_id, "meta": meta,
                "n_program_skills": len(skills),
                "n_job_skills": full["n_job_skills"], "n_overlap": full["n_overlap"],
                "full_coverage_pct": full["coverage_pct"],
                "role_coverage_pct": role_coverage_pct,
                "core_role_coverage_pct": core_role_coverage_pct,
                "weighted_role_coverage_pct": weighted_core_coverage_pct,
                "core_n_job_skills": core_n_job_skills, "core_n_overlap": core_n_overlap,
                # len(gap_skills_sorted) here is the true count before the [:100]
                # truncation applied at insert time below — core_n_job_skills -
                # core_n_overlap, i.e. every core skill not covered, not just the
                # ones that end up with a stored GapSkill row.
                "core_n_gap": len(gap_skills_sorted) if core_role_coverage_pct is not None else None,
                "gap_skills": gap_skills_sorted,
            })

        if dry_run:
            print("\nDry run — sample results (not written to DB):")
            for r in sorted(results, key=lambda x: -(x["core_role_coverage_pct"] or 0))[:15]:
                m = r["meta"]
                core = r["core_role_coverage_pct"]
                weighted = r["weighted_role_coverage_pct"]
                print(f"  {m['university'][:30]:30s} {m['name'][:40]:40s} {m['degree']:10s} "
                      f"full={r['full_coverage_pct']:5.1f}%  role={r['role_coverage_pct'] if r['role_coverage_pct'] is not None else 0:5.1f}%  "
                      f"core={core if core is not None else 'n/a':>5}  weighted={weighted if weighted is not None else 'n/a':>5}")
            return None

        # ── Write a new run ───────────────────────────────────────────────
        run_key = f"{RUN_KEY_PREFIX}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        run = AlignmentRun(
            run_key=run_key,
            experiment="LLM_desc_semantic",
            esco_version="n/a (direct)",
            job_snapshot_date=max_posting_date or JOB_SNAPSHOT_DATE_FALLBACK,
            n_active_postings=n_active_postings_total,
            is_canonical=False,
            status="complete",
            notes=(
                f"Live recompute matching the original notebook methodology exactly: cosine>={SIMILARITY_THRESHOLD} "
                "bidirectional with blocklist/allowlist, core skill = appears in >="
                f"{CORE_SKILL_FREQ_PCT*100:.0f}% of role postings, multi-role core sets unioned (not averaged). "
                + ("Restricted to the original 650 postings for validation. " if validate_650 else "")
                + (f"{n_unknown_posting_date} of {n_active_postings_total} active postings have no known "
                   "posting_date and are excluded from the date range shown to users. "
                   if n_unknown_posting_date else "")
            ),
        )
        session.add(run)
        session.flush()

        gap_skill_rows: list[tuple] = []
        for r in results:
            result = AlignmentResult(
                run_id=run.id, program_id=r["program_id"],
                n_program_skills=r["n_program_skills"], n_job_skills=r["n_job_skills"],
                n_overlap=r["n_overlap"], full_coverage_pct=r["full_coverage_pct"],
                role_coverage_pct=r["role_coverage_pct"],
                core_role_coverage_pct=r["core_role_coverage_pct"],
                core_n_job_skills=r["core_n_job_skills"], core_n_overlap=r["core_n_overlap"],
                core_n_gap=r["core_n_gap"],
                weighted_core_coverage_pct=r["weighted_role_coverage_pct"],
            )
            session.add(result)
            session.flush()
            for skill, freq in r["gap_skills"][:100]:
                gap_skill_rows.append((result.id, skill, freq, "uncertain"))

        from server.seed import bulk_insert
        bulk_insert(session, "gap_skills", ["result_id", "skill_name", "job_frequency", "gap_type"], gap_skill_rows)

        session.commit()
        print(f"\nWrote run '{run_key}' ({len(results)} programs). Not marked canonical — "
              f"review before promoting (see pipeline.promote_run).")
        return run_key
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--university", default=None, help="Limit to one university (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Print results, don't write to the DB")
    parser.add_argument("--validate-650", action="store_true",
                         help="Restrict to the original 650 postings to compare against thesis-published numbers")
    args = parser.parse_args()
    compute_alignment(university=args.university, dry_run=args.dry_run, validate_650=args.validate_650)


if __name__ == "__main__":
    main()
