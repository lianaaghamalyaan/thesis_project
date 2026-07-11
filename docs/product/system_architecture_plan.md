# CurriculumLens — Full System & Product Plan (Live Product)

Status: planning document, July 2026.
Builds on: `data_pipeline_architecture.md` (data model — still valid), `implementation_plan.md` (MVP scope), `information_architecture.md` (UX).

This document plans the **always-current product**: scheduled job scraping (every 2 weeks), curriculum refresh (every 6 months), automated analysis and suggestions after every refresh, and the backend/server architecture to run it as a product for universities and education-policy users.

---

## 1. What we are building

One system, two product surfaces:

1. **University product** — a university logs in and sees **only its own programs**: alignment scores, strengths, gaps (curriculum vs. documentation), suggestions, job-fit, and how everything changed since the last data refresh. Cross-university data informs their benchmarks and suggestions in the backend, but competitors are never named. Sold per university, per year.
2. **Policy view** — **all universities on the platform, named, program-level**: skill demand by role group over refreshes, program supply vs. market demand, university and program comparison, national gaps. Sold/offered to ministry, accreditation bodies (ANQA), donors (World Bank/EU education projects). Same data, different lens; it costs little extra and strengthens the "education policy" positioning.

What each account sees is decided at login by `organization.type` — full visibility matrix in §9.

The core promise: **"always up to date, never a one-off study."** Every claim in the UI is traceable to a dated run.

---

## 2. Refresh cadences (the heartbeat)

| What | Cadence | Trigger | Cost driver |
|---|---|---|---|
| Job scraping | Every 2 weeks | Scheduler | Nearly free (HTTP) |
| Job skill extraction | Same run, **new postings only** | After scrape | LLM tokens (small, see §8) |
| Alignment recompute + suggestions | Same run | After extraction | Pure computation, free |
| Curriculum refresh | Every 6 months per university | Semi-automated + manual intake | Human time, small LLM cost |
| ESCO taxonomy | Yearly check | Manual | None |

Key principle: **the expensive LLM work is incremental**. Only new postings are extracted; already-extracted postings keep their skills. Curriculum extraction reruns only for courses whose description text hash changed. Alignment itself is cheap set math and reruns fully every cycle.

**Rolling market window:** the "current market" = postings with `last_seen_at` within the last 90 days OR still active. A biweekly scrape keeps this window honest: a posting not seen for 2 consecutive runs (28 days) is marked inactive.

---

## 3. System overview

```
                      ┌──────────────────────────────────────────────┐
                      │                 SCHEDULER                     │
                      │   biweekly: collect → extract → align →      │
                      │   suggest → publish run → notify             │
                      └───────┬──────────────────────────────────────┘
                              │
   17 scrapers (pipeline/) ───▼
   job.am, staff.am, myjob.am,      raw files (append-only)
   14 company portals          →    data/raw/jobs/[source]/[date]/
                              │
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │  entities from
                    │                  │  data_pipeline_architecture.md:
                    │  job_posting     │  + external_id dedup
                    │  job_skill_extr. │  + first/last_seen, is_active
                    │  course / prog.  │  + curriculum_version
                    │  alignment_run   │  + is_canonical
                    │  alignment_result│
                    │  gap_skill       │
                    │  suggestion      │  ← new (§7)
                    │  org / user      │  ← new (§9)
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   FastAPI backend │  REST + auth + tenant isolation
                    └────────┬─────────┘
                             │
              ┌──────────────┴───────────────┐
              ▼                              ▼
      University dashboard            Policy dashboard
      (per-tenant login)              (aggregate view)
```

---

## 4. Tech stack (opinionated choices, with reasons)

| Layer | Choice | Why (and why not alternatives) |
|---|---|---|
| Database | **PostgreSQL 16** | The data model in `data_pipeline_architecture.md` is relational; multi-tenant filtering needs a query layer; JSON columns cover run parameters. SQLite would work for one tenant but not for concurrent web access. |
| ORM / migrations | **SQLAlchemy + Alembic** | Standard, boring, works. |
| Backend API | **FastAPI** | Python end-to-end (pipeline is already Python), async, typed, automatic OpenAPI docs (Phase 4 "API access" comes for free). Django is heavier than needed; Flask lacks the free API docs. |
| Scheduler | **Cron on the server calling `pipeline/run_all.py`** (Stage A) → **APScheduler inside a worker container** (Stage B) | Airflow/Prefect/Dagster are overkill for 1 biweekly DAG of 5 steps. A single orchestrator script with per-step logging + retry, run by cron, is debuggable by one person. Revisit only if pipelines multiply. |
| Frontend (pilot) | **Keep Streamlit**, add auth | The current dashboard is good enough to sell pilots. Rewriting UI before the first paying customer is the classic mistake. |
| Frontend (product) | **Next.js + React**, consuming the FastAPI | Trigger for the rewrite: first signed customer OR when Streamlit's per-session model hurts (concurrent users, custom branding, Armenian/English i18n). Not before. |
| LLM | **Claude API** — Haiku 4.5 for posting skill extraction (high volume, simple task), Sonnet for course extraction & suggestion narratives (low volume, quality matters) | Matches the thesis method (LLM extraction won). Model version is recorded per run for reproducibility. |
| Embeddings / ESCO matching | Keep the existing sentence-transformer ESCO index; load once in the worker | Already built and validated in the thesis. |
| Deployment | **One VPS (Hetzner/DO, 4 GB), Docker Compose**: `postgres`, `api`, `dashboard`, `worker` | Total infra ≈ €10–20/mo. No Kubernetes; nothing here needs to scale horizontally for years. Armenian universities won't demand AWS. |
| Object storage / backup | Nightly `pg_dump` + `data/raw/` sync to Backblaze B2 or Hetzner Storage Box | Raw data is the irreplaceable asset (per `docs/feedback_data_safety.md`). |
| Monitoring | Healthchecks.io ping from the pipeline + Telegram/email alert on scraper failure | A scraper silently dying is the #1 operational risk (§12). |

---

## 5. The biweekly pipeline run (step by step)

One orchestrator (`pipeline/run_all.py`, evolving the existing `run_collection.py`), five steps, each idempotent and separately re-runnable:

**Step 1 — Collect.** Run all 17 scrapers (already exist). Each writes raw files to `data/raw/jobs/[source]/[date]/` (append-only) and returns parsed postings. Per-source failures are recorded in `job_collection` and do **not** abort the run — a run is `partial` if ≥1 source fails, `failed` only if the aggregators (job.am, staff.am, myjob.am) all fail.

**Step 2 — Ingest & dedup.** Match postings to existing rows by `external_id` (source-specific ID or URL hash; fallback: hash of `company + title + normalized text`).
- Seen before → update `last_seen_at`.
- New → insert with `first_seen_at = now`, run the existing IT filter + role-group classifier.
- Existing active posting not seen in this run **and** not seen in the previous run → `is_active = False`. Never delete.

**Step 3 — Extract (incremental).** For new IT postings only: LLM skill extraction (same prompt family as the thesis pipeline) → ESCO normalization via the existing embedding index → rows in `job_skill_extraction` tagged with model version + prompt version.

**Step 4 — Align.** Create a `job_snapshot` (the 90-day active window). For every program in every active curriculum version: recompute coverage, gaps, surplus, role-aware and core metrics — exact same math as the thesis, now parameterized by snapshot. Classify each gap as curriculum/documentation/uncertain using `course_skill_extraction.confidence_tier`. Write `alignment_run` (status `pending_review` → see publish step) + results + gap skills.

**Step 5 — Suggest, diff, publish.**
- Run the suggestion engine (§7) and generate per-program narrative summaries.
- Compute the **delta vs. previous canonical run**: score changes, new gaps, closed gaps, new in-demand skills, biggest movers. Store as `run_diff` JSON — this powers the "what changed" panel, which is the feature that makes the product feel alive.
- Sanity gates before flipping `is_canonical`: n_active_postings within ±40% of previous run; no program score moved >20 pts without a curriculum change; all role groups still represented. If a gate fails, the run stays non-canonical and the operator gets an alert with the diff. **The dashboard never silently shows a broken run.**
- On publish: dashboard freshness banner updates automatically; optional email digest to university accounts ("Your March→April refresh: 2 programs improved, 3 new high-demand skills in Data/ML").

**Step 6 — Curriculum refresh (every 6 months, separate trigger).** Per university: re-scrape program pages where scrapers exist; otherwise send the curriculum intake template (Excel matching `final_curriculum_dataset.csv` schema) to the university contact. Diff by `(course_code, description_hash)`; re-extract skills only for new/changed courses; create a new `curriculum_version`; next biweekly run picks it up. Include the **description quality report** with every intake — flags courses with thin/missing descriptions. This is both onboarding QA and the documentation-gap upsell.

---

## 6. Database — deltas from the existing data-model doc

`data_pipeline_architecture.md` entities carry over as-is. Additions:

```
organization        org_id, name, type (university | policy | internal), plan, created_at
app_user            user_id, org_id FK, email, password_hash, role (org_admin | viewer | superadmin), last_login_at
university.org_id   FK → organization   (which org may see this university's private views)
suggestion          suggestion_id, run_id FK, program_id FK, kind (documentation | curriculum |
                    strategy | note), priority (high | medium | info), skill_names JSON,
                    rationale TEXT, narrative TEXT, status (proposed | accepted | dismissed | done)
run_diff            run_id FK, previous_run_id FK, diff JSON, created_at
prompt_version      version_id, task (job_extract | course_extract | narrative), prompt_text,
                    model_id, created_at        ← reproducibility for the LLM layer
```

`suggestion.status` is important: letting a program director mark a suggestion "accepted/done" creates the feedback loop ("you acted on X in April; the June run shows the gap closed") — the strongest possible renewal argument.

Migration of existing data: one script loads the frozen March 2026 CSVs into Postgres as `curriculum_version = v1`, `job_snapshot = march_2026_static`, `alignment_run = march_2026_static (is_canonical until first live run)`. The thesis snapshot becomes run #1 in the history, and nothing about the frozen files changes.

---

## 7. Suggestion engine (analysis → advice, without fake precision)

Two layers, deliberately:

**Layer 1 — deterministic rules** (auditable, no LLM):
| Condition | Suggestion kind | Example output |
|---|---|---|
| Program doc-quality score ≤ 0.20 and gap skill has a related course by embedding similarity | documentation, high | "Docker appears absent, but 'Distributed Systems' likely covers adjacent content — update its description before changing curriculum." |
| Gap skill in top-decile job frequency for the program's roles, no related course | curriculum, high | "Kubernetes appears in 34% of DevOps postings; no YSU course evidences it. Candidate for a new module." |
| Cluster of ≥3 gaps in one category (e.g., all Cloud) | strategy, medium | "Gaps cluster in Cloud/DevOps — a single elective could close several at once." |
| Skill taught in another program at the same university | curriculum, medium | "Taught in 'Applied Statistics' (Master) — consider cross-listing." |
| Gap skill taught in ≥2 role-matched peer programs at *other* universities (backend-only cross-university check; peers never named in university-facing output — see §9) | curriculum, high | "3 comparable programs in Armenia already teach this — a closable gap, not market noise." |
| Surplus skills with zero market demand | note, info | Framed neutrally: may be foundational/academic by design. |
| Gap trend: frequency rose ≥50% across last 3 runs | curriculum, high | "Demand for LLM engineering has doubled since March." |

**Layer 2 — LLM narrative** (Sonnet, once per program per run, cached): turns the rule outputs into 3–5 sentences of readable, constructive prose for non-technical leadership. The LLM **never invents suggestions** — it only verbalizes Layer 1 outputs. Narrative is stored on the run (versioned, reproducible), not generated live in the UI.

Framing rules (constitutional for the product): always lead with strengths; documentation gaps before curriculum gaps; every suggestion carries its evidence (job frequency, source run); no percent-precision beyond one decimal; scores 30–60% framed as normal, per CLAUDE.md.

---

## 8. LLM cost model (why "live" is affordable)

**Correction (2026-07-10):** the original draft of this section assumed 17,184 accumulated postings, based on a `wc -l` line count of `final_jobs_dataset_it_only.csv`. The file's job descriptions contain embedded newlines, so the true row count — verified by parsing, not counting lines — is **753 postings from 13 sources**, all collected as a single one-time snapshot in March 2026, not accumulated incrementally. That means we do not yet have real data on biweekly influx rate; the estimate below is a rough placeholder, not derived from observed accumulation, and must be treated as such until Stage A produces two live runs to measure the actual delta.

Placeholder assumption: an initial biweekly influx in the range of **50–150 new IT postings** (bottom of the original guess, scaled down proportionally since the true base is ~4.4% of the assumed size) — treat this as a guess to be replaced with a measured number after the first two live runs, not as a planning input.

- Job extraction: ~150 postings × ~1.5K input tokens, Haiku 4.5 ⇒ **well under $1 per biweekly run**.
- Narratives: 44 programs × ~2K tokens, Sonnet ⇒ **< $2 per run**.
- Curriculum re-extraction: only changed courses, twice a year ⇒ negligible.

**Total LLM cost is very likely under $10/month; total system ≈ $25–40/month** (infra cost is fixed regardless of posting volume). The "near-zero marginal cost" framing for the sales deck still holds directionally, but do not quote a specific postings-per-run number publicly until it's measured — the dataset's real growth rate is currently unknown.

---

## 9. Auth, multi-tenancy & the visibility model

**Core principle (decided 2026-07-11): all universities' data lives in one shared backend and every computation may use all of it — visibility is a presentation-layer filter that depends on who logs in, never a data-layer split.** This is what makes the product smarter than a single-tenant tool: a university's recommendations are informed by every other program on the platform, even though the university never sees competitors' data directly.

### Who sees what

| Account type | Program-level detail | Cross-university views | Purpose |
|---|---|---|---|
| **Policy** (ministry, ANQA, donors) | **All universities, all programs, named** | Full: rankings, aggregate skill supply vs. market demand, gaps by institution, national trends | System-level oversight: "where does the country's IT education stand vs. its labor market" |
| **University** (`org_admin`, `viewer`) | **Own university only** | Anonymized only: "peer average (n=6)", "best peer observed", "2 comparable programs in Armenia teach X" — never a named competitor | Improve own programs without competitive exposure |
| **Superadmin** (operator) | Everything | Everything + run management, data health | Operations |

### How cross-university data powers a university's own view (backend-only usage)

The university user never sees another university's name, but their view is computed *from* the full dataset:

1. **Peer benchmarks** (already live in `dashboard/src/benchmark.py`): score vs. anonymized average of role-matched peer programs.
2. **Suggestion evidence**: "this gap skill is covered by N comparable programs elsewhere in Armenia" — strong evidence a gap is closable at the curriculum level, not just market noise. Extends the §7 rule table with a cross-university rule: *gap skill taught in ≥2 peer programs at other universities → curriculum suggestion, priority boosted, evidence: anonymized count.*
3. **Documentation-quality calibration**: a program's doc-confidence score shown relative to the platform distribution ("your course descriptions are thinner than 75% of comparable programs") — turns the documentation-gap concept into an actionable, non-punitive nudge.
4. **Realistic targets**: "best peer observed: 31.2%" grounds expectations better than a theoretical 100%.

### Rules that make this safe to sell

- Anonymized peer stats are only shown when **n ≥ 3** role-matched peers exist (already enforced as `MIN_ROLE_MATCHED_PEERS = 3` in `benchmark.py`); below that, fall back to degree-level matching so small groups can't be reverse-identified.
- Policy accounts seeing named program-level detail is defensible because the underlying inputs are public (published curricula, public job postings) — but make it contractual: each university's platform agreement states that aggregate + named-program views are visible to policy-tier accounts. Universities knowing about (and agreeing to) the policy tier upfront avoids the "you sold our data" conversation later; framing it as "your ministry sees the same constructive framing you do — strengths first" matters.
- Enforcement lives in **one repository layer** (every query resolves the session's `org_id` + role and applies the visibility filter there), not per-endpoint — one place to audit, one place to test.

### Rollout

- Stage A (pilot): dashboard behind basic auth (Caddy/nginx) — one shared YSU login. Days of work.
- Stage B (product): FastAPI session/JWT auth with the role model above. `organization.type` (`university | policy | internal`) selects the view; YSU account + demo accounts for 2–3 prospect universities + one demo policy account (the policy view doubles as the strongest sales demo for ministries and accreditation bodies).
- The dashboard grows a **university switcher for policy/superadmin accounts only**; university accounts have no switcher at all — their university is resolved from the login, and the UI simply *is* their university (current YSU-hardcoded pages become the template).

## 10. API surface (Phase 4 seed, exists from Stage B)

```
GET  /api/programs                      → list w/ current scores (org-scoped)
GET  /api/programs/{id}                 → detail: score, strengths, gaps, suggestions, diff
GET  /api/programs/{id}/history         → score across runs
GET  /api/runs/current | /api/runs      → freshness + run registry
GET  /api/market/skills?role=...        → demand (policy + job-fit)
POST /api/suggestions/{id}/status       → accept/dismiss/done
POST /api/curriculum/intake             → upload filled template → validation report
```

---

## 11. Build sequence (concrete, ordered — status updated 2026-07-11)

**Stage A — "It breathes" (≈ 2–3 weeks). Goal: second live data point.**
1. ✅ **DONE** — Stable `job_id` (sha1 of `source_url`) added to the jobs CSV via `pipeline/migrations/001_stable_job_id.py`; skills remapped to `job_skills_by_id.json`; row-position join removed from `dashboard/src/data_loader.py` and both `generate_ysu_report*.py`. Coverage gap (650/753 postings extracted) is disclosed in the UI.
2. ☐ Wrap existing scrapers with per-source error capture + `job_collection` logging; dedup/active-inactive logic. (`pipeline/run_collection.py` orchestrator exists; needs the dedup-by-job_id and active/inactive layer.)
3. ◐ **Script written, not yet run** — `pipeline/extract_job_skills.py`: incremental LLM extraction for postings missing from `job_skills_by_id.json` (currently 103). Idempotent; needs `ANTHROPIC_API_KEY`. Dry-run verified.
4. ☐ Alignment as a parameterized function of (curriculum_version, job_snapshot) → writes `data/runs/[date]/` (still files, no DB yet). **Blocker discovered:** the code that produced `alignment_results.csv` is not in the repo — it must be reconstructed from the thesis notebooks (`notebooks/3_analysis/05_esco_normalization.ipynb` + `06_alignment_analysis.ipynb`) into a runnable pipeline module before any rerun is possible.
5. ◐ **Partially done** — freshness banner (with stale-data warning) and skill-coverage disclosure are live on the Overview page. Remaining: run-diff computation ("what changed" panel) — needs a second run to exist first.
6. ☐ Cron on the VPS + Healthchecks.io + Telegram alert. Run it twice → **demo the delta to YSU**.

**Stage B — "It's a product" (≈ 4–6 weeks).**
7. ☐ Postgres + migration script for all frozen data; pipeline writes to DB; dashboard reads via FastAPI.
8. ☐ Auth + org isolation; YSU account + demo accounts for 2–3 prospect universities (their data already exists!).
9. ☐ Suggestion engine (rules → table → narrative); suggestion status tracking. (A basic recommendations page exists in the dashboard; the rules engine in §7 formalizes it.)
10. ☐ Curriculum intake template + validation + description-quality report (onboarding kit).
11. ◐ **Partially done** — per-program PDF export is live on Program Detail (score, benchmark vs. peer average, documentation quality, strengths, gaps; browser-verified 2026-07-11). Peer-benchmark panel is also live in the UI (`dashboard/src/benchmark.py`). Remaining: include suggestions + run-diff in the PDF; Armenian localization.

**Stage C — "It sells" (ongoing).**
12. ☐ Policy dashboard (aggregates, trends across runs).
13. ☐ Next.js frontend when first customer signs / branding demands it.
14. ☐ Historical trend views once ≥4 runs exist; email digests; self-service onboarding last.

**Environment note:** the dashboard must be run from `.venv_dashboard/` (`./.venv_dashboard/bin/streamlit run dashboard/app.py`) — the system Anaconda Python has a broken NumPy 2 / xarray combination that crashes `plotly.express`. This also decides the deployment story: the Docker image (§4) pins its own clean dependency set, which is exactly what prevents this class of failure in production.

## 12. Risks & honest mitigations

| Risk | Reality | Mitigation |
|---|---|---|
| Scraper rot | #1 operational cost; sites change HTML monthly | Per-source isolation, alerting, `partial` runs acceptable; budget ~2h/month maintenance; aggregators (job.am/staff.am) are the load-bearing sources — prioritize their stability |
| Scraping ToS | Company career pages: low risk. Aggregators: check ToS; prefer RSS/APIs where offered | Get written permission where possible — "official data partner" is also a sales asset in a small market |
| Seasonality read as signal | Armenian IT hiring dips in summer | Show posting-volume context next to every trend; compare year-over-year once data exists; never show a trend without its n |
| LLM/prompt drift across runs | Score changes could be artifacts | `prompt_version` table; on any model/prompt change, re-run previous snapshot and report the methodological delta separately from the market delta |
| Curriculum staleness (6-month cadence slips) | Universities are slow | Product stays honest: curriculum version date always visible; nagging is automated (email at month 5) |
| One-person bus factor | You | Boring stack, one VPS, everything in Docker Compose, runbook in repo, nightly offsite backups |

## 13. What we deliberately do NOT build

- Kubernetes, microservices, Airflow, Kafka — nothing here needs them.
- Real-time scraping — biweekly is honest and cheap; "real-time" adds cost and legal exposure for zero decision-value (curricula change yearly).
- Automatic curriculum scraping of all universities — intake template + per-uni scrapers where easy; humans in the loop is fine at this scale.
- Score forecasting / predictions — fake precision; we report observed demand, not prophecy.
