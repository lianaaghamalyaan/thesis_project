# CLAUDE.md — Project Guide for AI-Assisted Development

## What this project is

This is a research-to-product codebase. It began as a master's thesis at Yerevan State University (YSU), investigating how well Armenian IT university programs align with the local labor market. The thesis work is complete. The codebase is now being evolved into a real decision-support product for university use, starting with YSU.

The product is called **CurriculumLens** (working title). It is a program-first dashboard that helps academic leadership — vice-rectors, curriculum committees, program directors, quality assurance staff — understand how their programs relate to labor market demand, what is strong, what is missing, and what to do about it.

## Current status (as of June 2026)

- Thesis data pipeline: **complete and frozen** — a static March 2026 snapshot
- Research dashboard (`dashboard/app.py`): **working but research-oriented** — experiment comparison UI, not user-facing
- Product planning docs: **just created** — see `docs/product/`
- Product implementation: **not started yet**

## What not to do

- Do not refactor or restructure the thesis notebooks (`notebooks/`) — they are the research audit trail
- Do not move or delete raw data files in `data/raw/` — see `docs/feedback_data_safety.md`
- Do not modify `docs/thesis/` — the written thesis chapters are finalized
- Do not treat the current `dashboard/app.py` as the target product — it needs to be redesigned around program-first UX
- Do not add fake precision to recommendations — the system should be useful, not overconfident

## Target users

Non-technical academic leadership:
- Vice-rector / prorector level
- Curriculum committees
- Program directors
- Quality assurance staff
- Possibly department heads and selected faculty (later)

They need to understand outcomes, not methodology.

## Product goals

Help users answer:
1. How well does this program align with current labor market demand?
2. What is this program already strong in?
3. What is missing or weak?
4. Why is the score what it is?
5. Is the gap a real curriculum gap, a documentation gap, or both?
6. How well does this program match a specific job or target role?
7. What realistic next steps could improve the program?

## Core architectural principles

1. **Program-first** — all views anchor on a program, not on experiments or methods
2. **Explanation-first** — scores always come with reasons; never just a number
3. **Reproducible** — every result must be traceable to a specific data snapshot and run
4. **Data-fresh** — the labor market side must stay current; the curriculum side updates with program input
5. **Tenant-ready** — designed for YSU first, expandable to other universities without a data migration
6. **Constructive** — always surface strengths alongside gaps; never punitive framing

## Glossary

| Term | Meaning |
|---|---|
| **Program** | A degree program, e.g. "Data Science in Business, Master" |
| **Course** | A single course within a program |
| **Alignment score** | Percentage of market-demanded skills that the program covers |
| **Core role-aware coverage** | Coverage against the skills demanded by roles most relevant to this program (the primary metric) |
| **Gap skill** | A skill demanded by the market that the program does not cover |
| **Surplus skill** | A skill the program teaches that the market does not demand in its relevant roles |
| **Curriculum gap** | A gap that is likely real — the skill is absent from course content |
| **Documentation gap** | A gap that may be artificial — the skill could be taught but is not mentioned in course descriptions |
| **Experiment** | One of 12 methodological variants (skill extraction method × input type × matching type). The canonical one is `LLM_desc_semantic`. |
| **ESCO** | European Skills, Competences, Qualifications and Occupations taxonomy (v1.2) used for skill normalization |
| **Role group** | A job-market role category (e.g. Software Engineering, Data / ML / AI, DevOps / Cloud) |
| **Run / snapshot** | A specific execution of the alignment pipeline against a specific version of data |

## Core data files and schemas

All paths are relative to the repo root.

### `data/processed/curriculum/final_curriculum_dataset.csv`
1,545 rows. One row per course.

Key columns: `course_id`, `university`, `program_name`, `program_code`, `degree_level`, `course_code`, `course_name`, `course_name_original`, `credits`, `semester`, `description`, `source_language`, `notes`, `source_url`, `academic_year`

Universities present: YSU, AUA, NPUA, NUACA, RAU, UFAR, ASUE, ASPU (8 total, 44 programs)

### `data/processed/jobs/final_jobs_dataset_it_only.csv`
753 rows. One row per IT job posting. (Verified by parsing the CSV, not by `wc -l` — `full_text` contains embedded newlines, so the file has ~17,185 physical lines for 753 actual records. Earlier docs and the dashboard metadata quoted "17,184 postings," derived from `wc -l`; that number was never a real row count and has been corrected everywhere as of 2026-07-10.)

Key columns: `source`, `source_type`, `source_url`, `job_title`, `company_name`, `location`, `employment_type`, `seniority_level`, `posting_date`, `deadline`, `skills_tags`, `full_text`, `it_filter_decision`, `it_role_group`, `it_filter_reason`, `it_tech_text_score`

Role groups in `it_role_group`: Backend, Data / ML / AI, DevOps / Cloud, Frontend / JS, Full Stack, General IT, Hardware / Embedded, IT Support / Admin, Mobile, QA / Testing, Security, Technical Management, UX / Product Design

13 distinct sources (not 14 — also corrected).

Note: The broader `final_jobs_dataset.csv` includes non-IT jobs (1,369 rows). The IT-only file is the analysis set.

**Fixed 2026-07-10 — was a fragile join, now a stable one with known partial coverage:** `data/processed/jobs/final_jobs_dataset_it_only.csv` now has a `job_id` column (sha1 of `source_url`, added by `pipeline/migrations/001_stable_job_id.py`). `data/processed/unified/job_skills_by_id.json` (superseding the old positionally-keyed `job_skills_norm.json`) is keyed by `job_id` and covers 650 of 753 postings — the other 103 are from sources added after the last extraction run (betconstruct, nvidia, superannotate, teamviewer, griddynamics, plus more epam postings) and were never extracted. `dashboard/src/data_loader.py::load_job_skills_by_role()` and both `generate_ysu_report*.py` scripts now join on `job_id`, so they no longer silently mis-join — but the Strengths tab and Job Fit page still only reflect 650/753 postings until `pipeline/extract_job_skills.py` is run (requires `ANTHROPIC_API_KEY`, not yet run in this environment). The dashboard now discloses this coverage gap via `data_loader.job_skills_coverage()`.

**Unverified — do not assume:** whether `alignment_results.csv` and `gap_analysis.csv` (the canonical scores/gaps) were computed from the same partial 650-posting skill extraction or a separate, complete one is unknown — the code that produced those files is not in this repo. Don't claim alignment scores are "unaffected" by the coverage gap without checking; nobody has verified that.

### `data/processed/unified/alignment_results.csv`
528 rows. One row per (experiment × program).

Key columns: `experiment`, `method`, `input_type`, `matching`, `university`, `program`, `degree`, `relevant_roles`, `n_program_skills`, `n_job_skills`, `n_overlap`, `full_coverage_pct`, `n_gap`, `n_surplus`, `role_coverage_pct`, `core_role_coverage_pct`, `core_n_job_skills`, `core_n_overlap`, `core_n_gap`, `weighted_core_coverage_pct`

**Canonical experiment: `LLM_desc_semantic`** — use this as the default in all product views.

12 experiments exist: `{TFIDF,KeyBERT,LLM}_{names,desc}_{exact,semantic}`

### `data/processed/unified/gap_analysis.csv`
4,398 rows. One row per (program × gap skill).

Key columns: `university`, `program`, `degree`, `gap_skill`, `job_frequency`, `relevant_roles`

Note: This file currently lacks an `experiment` column — it is implicitly derived from `LLM_desc_semantic`.

### `data/processed/role_aware/program_role_mapping.json`
Maps each `"university | program | degree"` string to its relevant role group(s). Programs mapped to `"ALL"` are general programs with no role-specific targeting.

### `data/processed/unified/course_confidence_tiers.json`
**This is the key asset for documentation gap detection.** It assigns confidence tiers to course-skill mappings. Low-confidence mappings indicate that a skill may be present in the curriculum but is weakly evidenced by the course description — i.e., a likely documentation gap. High-confidence mappings indicate the skill is clearly described.

### `data/processed/unified/job_skills_norm.json`
Maps job index integers → normalized skill sets. The index must be joined back to `final_jobs_dataset_it_only.csv` by row position to get job title / company. Verify this join path before building job-fit features.

## Methodology summary (for context, not for UI)

The pipeline used three skill extraction methods (TF-IDF, KeyBERT, LLM) × two input types (course names only vs. full descriptions) × two matching methods (exact string vs. semantic ESCO embedding similarity). This produced 12 experiments. The best-performing one (`LLM_desc_semantic`) is the canonical result and the only one that should be shown to product users. The experiment comparison view belongs in an Evidence/Admin section, not in the main user flow.

AUA programs have a known description asymmetry: using names only gives ~5× lower coverage than using descriptions. This means programs with weak or missing course descriptions will show lower alignment scores even if the curriculum is strong — the description quality is a confounder. This is the basis of the documentation gap concept.

## Important domain assumptions

1. Alignment is measured against a March 2026 job market snapshot. Scores reflect that window.
2. ESCO v1.2 is used as the skill normalization layer. Skills outside ESCO vocabulary are in the emerging tech file.
3. Programs with no role-group mapping (mapped to "ALL") are compared against the full IT job market, not a targeted subset.
4. Coverage scores are expressed as percentage of job-market skills covered, not the reverse.
5. A score of 30-60% in `core_role_coverage_pct` is meaningful — not a failure. The market demands thousands of skills; no single program covers them all. Framing matters.

## Reproducibility requirements

Every alignment result must be traceable to:
- A specific version of the curriculum data
- A specific snapshot of job postings (with a date)
- The pipeline parameters used (experiment config)
- The ESCO version used

When the data refreshes, old results must be preserved, not overwritten.

## Data freshness requirements

- Job postings must be refreshed periodically (target: weekly or daily)
- Old postings should be marked inactive, not deleted
- The "current" alignment view should use a rolling recent window (e.g., last 90 days)
- Historical alignment runs must remain queryable
- Data freshness (last refresh date, number of active postings) must be visible in the dashboard

## Phased product direction

**Phase 1 (now): YSU-first MVP**
- Single university view (YSU)
- Program list → program detail → strengths/gaps/recommendations
- Job-fit comparison feature
- Documentation gap vs curriculum gap distinction
- Static data from thesis snapshot (with manual refresh path)

**Phase 2: Multi-university expansion**
- Add other universities from existing data (AUA, NPUA, NUACA, etc.)
- Login / access control per university
- Organization-isolated views

**Phase 3: Live pipeline**
- Automated job collection
- Scheduled pipeline reruns
- Data freshness tracking in UI
- Historical trend views

**Phase 4: SaaS**
- Multi-tenant architecture
- Self-service onboarding
- API access for institutional data integration

## What the thesis dashboard (`dashboard/app.py`) currently has

See `docs/product/implementation_plan.md` — Codebase Assessment section.

## File locations for product planning docs

- `docs/product/implementation_plan.md` — implementation plan + codebase assessment
- `docs/product/information_architecture.md` — page structure and UX
- `docs/product/data_pipeline_architecture.md` — data model and pipeline design
