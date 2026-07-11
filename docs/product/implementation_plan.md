# Implementation Plan — CurriculumLens Product

## Product goals

Build a program-first, decision-support dashboard for academic leadership at Armenian universities, starting with YSU. Users are non-technical. They need to understand alignment outcomes, not methodology.

Primary questions the product must answer:
1. How well does this program align with current market demand?
2. What is already strong?
3. What is missing or weak, and why?
4. Is the gap real (curriculum) or representational (documentation)?
5. How well does this program fit a specific job/role?
6. What realistic next steps could improve the program?

---

## Codebase assessment

### What exists and is reusable

**Data layer — strong foundation**
- `data/processed/curriculum/final_curriculum_dataset.csv` — 1,545 courses, 8 universities, 44 programs. Clean schema. Ready to use.
- `data/processed/unified/alignment_results.csv` — 528 rows covering 12 experiments × 44 programs. The `LLM_desc_semantic` experiment is the canonical result.
- `data/processed/unified/gap_analysis.csv` — 4,398 gap-skill rows per program. Ready to drive the "what's missing" view.
- `data/processed/role_aware/program_role_mapping.json` — maps programs to relevant role groups.
- `data/processed/jobs/final_jobs_dataset_it_only.csv` — 753 IT jobs with role labels (corrected 2026-07-10; the "17,184" figure in older docs was a `wc -l` line count, not a row count — `full_text` has embedded newlines).
- `data/processed/unified/course_confidence_tiers.json` — **this is the documentation gap signal**. Already computed; needs to be surfaced in the product UI.

**Dashboard utilities — partially reusable**
The utility functions in `dashboard/app.py` are clean and reusable:
- `load_csv`, `load_optional_csv` — simple cached CSV loaders
- `apply_multiselect`, `search_text` — generic filter helpers
- `UNI_SHORT` mapping dictionary
- Chart functions (`chart_top_gaps`, `chart_university_coverage`) — can be adapted

### What is broken

**Resolved:** the missing `final_jobs_dataset_it_with_roles.csv` dependency described in earlier drafts of this doc no longer exists in the codebase — the dashboard was rebuilt as a multi-page `dashboard/pages/` app that reads `final_jobs_dataset_it_only.csv` directly via `dashboard/src/data_loader.py`. Confirmed by grep against the current source (2026-07-10).

**Live: fragile row-position join.** `dashboard/src/data_loader.py::load_job_skills_by_role()` joins `data/processed/unified/job_skills_norm.json` (only 650 entries, keyed by integer row position) against `final_jobs_dataset_it_only.csv` (753 rows) by `.iloc[idx]`. This silently returns partial/wrong data for the Strengths tab and Job Fit page rather than crashing. This is the actual first fix needed — see Stage A of `system_architecture_plan.md`.

**Also corrected:** the dashboard and generated PDF reports previously displayed "17,184 IT job postings" — that number was a `wc -l` line count (job descriptions contain embedded newlines), not a row count. The true figure is 753 postings from 13 sources. Fixed in `data/runs/march_2026_static/metadata.json` and both `generate_ysu_report*.py` scripts on 2026-07-10; any already-generated `ysu_alignment_report*.pdf/.docx` files predate the fix and should be regenerated before further distribution.

### What is thesis/research-specific (needs to move out of main flow)

- The experiment selector (12 variants) — belongs in an Evidence/Admin section, not the main UX
- The "Reuse Guide" page — remove from product, keep as a separate README
- Method comparison charts — research artifact, not decision support
- The `experiment` column filter in the Alignment Results page — hide; always use `LLM_desc_semantic` by default
- The `Visual Summary` page duplicates other pages — merge into Overview or remove

### What needs to be redesigned

- **Navigation model**: sidebar radio buttons → program-first entry point
- **Overview page**: currently shows dataset composition and job source charts (research context). Product Overview should show program portfolio at a glance.
- **Alignment Results page**: currently anchors on experiment selection. Should anchor on program selection with metrics explained.
- **No YSU-first filter**: all universities shown equally. Product should default to a single university context.
- **No recommendations layer**: gaps are listed but no prioritization or action framing.
- **No documentation gap signal**: `course_confidence_tiers.json` is never surfaced.
- **No job-fit feature**: no page for comparing a program against a specific role or job description.
- **No login/access control**: open access, single-tenant assumption.
- **No data freshness indicators**: no metadata about when data was last updated.

### What data assumptions currently don't work for a live product

1. **Static snapshot**: data is frozen at March 2026. There is no refresh mechanism.
2. **No job posting timestamps used** for recency filtering: `posting_date` exists but is not used to define a "current" window.
3. **No run versioning**: `alignment_results.csv` is a single file; no history of past runs.
4. **Job skills are keyed by integer index**: `job_skills_norm.json` uses integer keys. The join back to job title/description via row position is fragile — it breaks if the job file is ever reordered or filtered.
5. **No curriculum version tracking**: if course descriptions are updated, there is no way to know when or compare old vs. new.
6. **Gap analysis has no `experiment` column**: it is implicitly `LLM_desc_semantic` but this is not recorded in the file itself.

---

## MVP scope (Phase 1)

**Goal**: A working product for YSU that is demo-ready and can be shared with university stakeholders.

**In scope:**
- Program list view (YSU programs)
- Program detail view: score, strengths, gaps, documentation gap signal
- Job-fit comparison: program vs. target role (from role group list)
- Recommendations panel (priority gaps with framing)
- Evidence view: how the score was computed, data snapshot date
- Data admin view: data freshness status, last run date
- Fix the broken `final_jobs_dataset_it_with_roles.csv` dependency

**Out of scope for MVP:**
- Automated job collection / pipeline scheduling
- Login / access control
- Multi-university views
- Paste-a-job-description feature (use role group selection instead)
- Historical trend charts
- Editable curriculum input

**Deliberate simplifications for MVP:**
- Use the existing static March 2026 data snapshot
- Show YSU programs only (filter at the product layer; do not restructure data)
- Use `LLM_desc_semantic` as the only experiment (no experiment selector in main flow)
- No backend — keep as a Streamlit app with flat-file data loading

---

## Phased rollout

### Phase 1 — YSU MVP (now)
- Fix broken dependency
- Redesign navigation to program-first
- Build Program List page
- Build Program Detail page with explanation layer
- Build Job-Fit Comparison page (program vs. role group)
- Build Recommendations panel
- Build Evidence page
- Build Data Admin / Freshness page
- Deploy internally for YSU review

### Phase 2 — Multi-university expansion
- Add other universities from existing data
- Add login and role-based access (per-university isolation)
- Admin user type can see all universities; university users see their own
- Deploy to hosting (Streamlit Cloud, Railway, or dedicated server)

### Phase 3 — Live pipeline
- Automated periodic job scraping (weekly or daily)
- Job deduplication and active/inactive tracking
- Rolling 90-day job window for "current" alignment
- Pipeline scheduler (cron or cloud scheduler)
- Data freshness dashboard
- Alignment reruns triggered when data is refreshed
- Run versioning and history

### Phase 4 — SaaS foundation
- Multi-tenant data isolation
- University self-service onboarding
- API for feeding in curriculum data
- Subscription / billing layer (if needed)
- Support for non-IT domains (law, medicine, etc.)

---

## Page-by-page product scope

See `docs/product/information_architecture.md` for full page definitions.

Summary:
1. **Overview** — portfolio health of all programs for the selected university
2. **Programs** — sortable list of programs with quick alignment scores
3. **Program Detail** — deep view of one program: score, strengths, gaps, gap type, recommendations
4. **Job Fit** — compare a program against a role or job description
5. **Recommendations** — cross-program priority list of what to improve
6. **Evidence** — methodology, data snapshot, run metadata (for trust and auditability)
7. **Admin** — data freshness, job collection status, pipeline run history

---

## Technical architecture direction

### For MVP (Phase 1)

Keep Streamlit. Do not over-engineer.

- Single `app.py` or multi-page Streamlit app using `st.navigation` / `pages/` directory
- Data loaded from CSV/JSON files in `data/processed/`
- All data transformations in a `src/` package, not inline in pages
- No backend API needed yet
- No database needed yet — flat files are sufficient for static data

Recommended project structure for Phase 1:

```
dashboard/
  app.py                  # entry point and navigation
  pages/
    01_overview.py
    02_programs.py
    03_program_detail.py
    04_job_fit.py
    05_recommendations.py
    06_evidence.py
    07_admin.py
  src/
    data_loader.py        # all CSV/JSON loading with caching
    alignment.py          # alignment score queries and formatting
    gaps.py               # gap analysis queries
    recommendations.py    # recommendation logic
    job_fit.py            # job-fit comparison logic
    doc_gap.py            # documentation gap signal from confidence tiers
    formatting.py         # shared UI helpers and metric labels
  requirements.txt
```

### For Phase 3+ (live pipeline)

Move to a structured backend:
- FastAPI backend serving alignment data from a database
- PostgreSQL for structured storage (jobs, runs, alignment results)
- Object storage (S3 or equivalent) for raw job archives
- Celery + Redis or a cloud scheduler for pipeline jobs
- The Streamlit frontend calls the API rather than loading CSVs directly
- OR migrate the frontend to a proper web framework (React + FastAPI) at this stage

---

## Data model direction

See `docs/product/data_pipeline_architecture.md` for full data architecture.

Core entities:
- `University` — institution
- `Program` — degree program belonging to a university
- `Course` — course belonging to a program
- `CourseSkill` — skill extracted from a course (with confidence tier)
- `JobPosting` — job posting with metadata, role group, and scraped date
- `JobSkill` — skill extracted from a job posting
- `AlignmentRun` — versioned execution of the pipeline against a data snapshot
- `AlignmentResult` — per-program result for a given run
- `GapSkill` — gap skill record for a given program in a given run

---

## Build order (recommended)

1. Fix the `final_jobs_dataset_it_with_roles.csv` crash — unblocks development
2. Create the `src/` data layer (loaders, queries, gap logic) — everything else depends on this
3. Build Program List page — simplest page, validates the data layer
4. Build Program Detail page — core product value
5. Build Job-Fit Comparison page — highest-priority feature from stakeholder input
6. Build Evidence page — needed for trust and institutional adoption
7. Build Recommendations panel — adds action layer to the detail and overview pages
8. Build Overview page — brings it all together
9. Build Admin / Data Freshness page — needed before any live demo
10. Deploy and get YSU feedback

---

## Biggest technical risks

1. **Job skills ↔ job index join is fragile**: `job_skills_norm.json` uses integer row indices. If job data is filtered or reordered, the join silently breaks. Fix before building job-fit features.
2. **No run versioning yet**: currently a single flat file. Building any historical or freshness UI requires designing a run versioning scheme first.
3. **Course confidence tiers need interpretation**: `course_confidence_tiers.json` exists but the logic for interpreting "high confidence = curriculum gap" vs. "low confidence = documentation gap" needs to be explicitly coded and tested.
4. **YSU course descriptions are in Armenian**: the NLP pipeline translated them, but the product UI will display the English translations. The quality of those translations varies. This affects perceived description quality.
5. **Static data for MVP means freshness is fake**: the MVP will show a static March 2026 snapshot. Be explicit in the UI about this — "Based on March 2026 job market data" — so it does not feel stale without explanation.

## Biggest product risks

1. **Scores without context feel punitive**: a 25% alignment score will alarm stakeholders unless it is explained that this is typical, what a "good" score looks like, and what the practical meaning is.
2. **Documentation gap distinction is subtle**: university staff may not immediately understand why "the score is low but we might already teach this." This needs careful UI copy.
3. **Stakeholder expectations around recommendations**: actionable recommendations require judgment, not just data. The product should not promise more than it can deliver — "these are likely gaps based on job market data" is the honest framing.
4. **Data freshness and trust**: if the data goes stale without being updated, university users will lose trust. A clear data freshness indicator is essential from day one.
5. **YSU-first scope may feel limited to leadership**: prepare a demo that shows how the system could expand to show inter-university benchmarking, even if that's Phase 2.

---

## Short-term tasks (to start implementation)

- [ ] Fix `final_jobs_dataset_it_with_roles.csv` crash (highest priority)
- [ ] Create `dashboard/src/` package structure
- [ ] Write `data_loader.py` with YSU-filtered views
- [ ] Define `AlignmentRun` metadata schema (even if MVP uses a static stub)
- [ ] Build Program List page
- [ ] Implement documentation gap logic from `course_confidence_tiers.json`
- [ ] Verify `job_skills_norm.json` index join path

## Later features

- Paste-a-job-description for ad-hoc job-fit (requires LLM call at query time)
- Program comparison (compare two YSU programs side by side)
- Curriculum editor (mark courses as updated, trigger partial rerun)
- Email digest for program directors (weekly alignment summary)
- Export to PDF for curriculum committee meetings
- Non-IT domain support
