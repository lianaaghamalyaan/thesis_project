# Data & Pipeline Architecture — CurriculumLens

## Design principles

1. **Raw data is never modified** — always preserved as-is from collection
2. **Normalized/cleaned data is stored separately from raw data**
3. **Every analysis run is versioned** — old results are not overwritten
4. **The "current" view is defined by a rolling window + explicit run reference**
5. **Freshness is always surfaced** — users can always see when data was last collected
6. **Active vs. inactive jobs** — postings are marked, not deleted
7. **Multi-university ready from the start** — all entities carry a `university_id`

---

## Current state vs. target state

| Concern | Current (March 2026) | Target (product) |
|---|---|---|
| Job data | Static CSV snapshot | Periodically refreshed, versioned |
| Job freshness | No tracking | Active/inactive flags, collection timestamps |
| Curriculum data | Static CSVs | Versioned, updatable per program |
| Alignment runs | Single flat file | Versioned runs with input snapshot references |
| Historical results | None | Preserved, queryable |
| Multi-university | All in one CSV | Filtered by `university_id` |
| Run reproducibility | Not tracked | Full input + config recorded per run |

---

## Core data entities

### University
```
university_id         UUID
name                  string
short_name            string
country               string
created_at            timestamp
```

### Program
```
program_id            UUID
university_id         FK → University
name                  string
degree_level          enum: Bachelor | Master | General
program_code          string (nullable)
is_active             bool
created_at            timestamp
updated_at            timestamp
```

### Course
```
course_id             UUID (currently integer in CSVs — migrate to UUID)
program_id            FK → Program
course_code           string
course_name           string
course_name_original  string (original language)
description           text (English translation if applicable)
description_original  text (original language)
credits               float
semester              float
component             string
source_language       string
source_url            string
academic_year         string
notes                 text
created_at            timestamp
updated_at            timestamp
```

### CourseSkillExtraction
```
extraction_id         UUID
course_id             FK → Course
curriculum_version_id FK → CurriculumVersion
skill_name            string (canonical)
esco_concept_id       string (nullable)
confidence_tier       enum: high | medium | low
extraction_method     enum: LLM | KeyBERT | TFIDF
input_type            enum: names | descriptions
created_at            timestamp
```

`confidence_tier` is the product-layer basis for the documentation gap signal. Low-confidence extractions mean course descriptions are vague, weak, or absent — indicating a potential documentation gap rather than a true curriculum gap.

### CurriculumVersion
```
curriculum_version_id UUID
university_id         FK → University
collected_at          timestamp
notes                 text
```

Allows tracking when curriculum data was last collected per university. Changes to course descriptions create new versions.

---

### JobSource
```
source_id             UUID
name                  string (e.g., "LinkedIn", "staff.am", "PicsArt")
source_type           enum: aggregator | company_portal | job_board
url                   string
```

### JobCollection
```
collection_id         UUID
collected_at          timestamp
source_id             FK → JobSource
n_postings_collected  int
n_new                 int
n_duplicates          int
n_failed              int
status                enum: success | partial | failed
notes                 text
```

Records every scraping run. This is the basis for freshness tracking.

### JobPosting
```
posting_id            UUID
source_id             FK → JobSource
collection_id         FK → JobCollection (the collection that first captured it)
external_id           string (source-specific ID for deduplication)
job_title             string
company_name          string
location              string
employment_type       string
seniority_level       string
industries            string
posting_date          date
deadline              date (nullable)
skills_tags           text
full_text             text
first_seen_at         timestamp
last_seen_at          timestamp
is_active             bool
is_it_job             bool
it_role_group         string
it_filter_reason      string
it_tech_text_score    float
```

`first_seen_at` and `last_seen_at` track the active window. `is_active` is set to False when the posting stops appearing in collection runs. Postings are **never deleted**.

**Current state**: The existing CSVs map cleanly to this schema. `posting_id` can be generated from row index for now; migrate to UUID-based on the next ingestion run.

### JobSkillExtraction
```
extraction_id         UUID
posting_id            FK → JobPosting
job_snapshot_id       FK → JobSnapshot
skill_name            string (canonical)
esco_concept_id       string (nullable)
extraction_method     enum: LLM | KeyBERT | TFIDF
created_at            timestamp
```

### JobSnapshot
```
snapshot_id           UUID
created_at            timestamp
window_days           int (e.g., 90)
n_active_postings     int
notes                 text
```

A JobSnapshot represents the set of active postings used for a specific alignment run. When data is refreshed, a new snapshot is created. Old snapshots are preserved so old runs remain reproducible.

---

### AlignmentRun
```
run_id                UUID
created_at            timestamp
experiment            string (e.g., "LLM_desc_semantic")
curriculum_version_id FK → CurriculumVersion
job_snapshot_id       FK → JobSnapshot
esco_version          string (e.g., "v1.2")
parameters            JSON (threshold, method config, etc.)
is_canonical          bool (True for the run shown in the product UI)
status                enum: pending | running | complete | failed
notes                 text
```

`is_canonical` marks which run is shown in the product. When a new run is created and validated, it is marked canonical. Old runs remain in storage.

**Current state**: The existing `alignment_results.csv` represents a single implicit run. For the MVP, create a stub `AlignmentRun` record that references the March 2026 snapshot, so the architecture is ready for multiple runs even before automation is built.

### AlignmentResult
```
result_id             UUID
run_id                FK → AlignmentRun
program_id            FK → Program
relevant_roles        string (comma-separated role groups)
n_program_skills      int
n_job_skills          int
n_overlap             int
full_coverage_pct     float
role_coverage_pct     float
core_role_coverage_pct float
core_n_job_skills     int
core_n_overlap        int
core_n_gap            int
n_foundational        int
n_surplus_clean       int
weighted_core_coverage_pct float
```

### GapSkill
```
gap_id                UUID
result_id             FK → AlignmentResult
run_id                FK → AlignmentRun
program_id            FK → Program
skill_name            string
job_frequency         int
relevant_roles        string
gap_type              enum: curriculum_gap | documentation_gap | uncertain
```

`gap_type` is computed at analysis time using `CourseSkillExtraction.confidence_tier` for adjacent skills. This is the field the product UI shows as the gap type indicator.

**Current state**: The existing `gap_analysis.csv` lacks a `run_id` and `gap_type`. These are two fields to add when the data model is formalized.

---

## Data flow

### Current (Phase 1 MVP — static)

```
data/raw/jobs/          ─┐
data/raw/university/    ─┤─→ data/processed/ ─→ dashboard reads CSVs directly
data/raw/esco/          ─┘
```

The dashboard reads flat files. No database. No scheduler.

### Target (Phase 3 — live)

```
Scraper jobs (scheduled)
    │
    ▼
data/raw/jobs/[source]/[date]/          ← raw, never modified
    │
    ▼
Ingestion pipeline
  - deduplication by external_id
  - IT filter
  - role group classification
    │
    ▼
JobPosting table                        ← normalized, versioned
    │
    ▼
Skill extraction pipeline
  - LLM skill extraction
  - ESCO normalization
    │
    ▼
JobSkillExtraction table + JobSnapshot  ← skill data, snapshotted

Curriculum update (manual or scraper)
    │
    ▼
Course table + CourseSkillExtraction    ← versioned

Alignment pipeline (triggered on new snapshot)
  - per-program coverage
  - gap analysis
  - gap type classification
    │
    ▼
AlignmentRun + AlignmentResult + GapSkill table

Dashboard reads from tables, not CSVs
```

---

## Reproducibility design

To reproduce any past result:

1. Every `AlignmentRun` records:
   - Exact `curriculum_version_id` (which courses and descriptions were used)
   - Exact `job_snapshot_id` (which postings were included, by `first_seen_at` / `last_seen_at` window)
   - Exact `parameters` JSON (threshold, method, ESCO version)
2. Raw job data is never deleted — it is always available at `data/raw/jobs/[source]/[date]/`
3. Processed outputs for each run are stored in a versioned path: `data/runs/[run_id]/`
4. The `is_canonical` flag on `AlignmentRun` controls what the product shows without deleting history

To reproduce a specific past result:
- Find the `run_id`
- Load the `curriculum_version_id` → get the course dataset used
- Load the `job_snapshot_id` → get the job set used
- Re-run the pipeline with the same `parameters`
- Compare outputs to stored `AlignmentResult`

---

## Data freshness model

### Job postings

- **Active**: posting was present in the last collection run
- **Inactive**: posting has not appeared in collection for more than N days (default: 14)
- **Window**: the "current market" view uses postings where `is_active = True` OR `last_seen_at` is within the last 90 days

### Freshness dashboard indicators

The Admin page shows:
- `last_seen_at` of the most recent posting per source
- Days since last collection per source
- Number of active vs. inactive postings
- Health status: green (< 7 days), amber (7-30 days), red (> 30 days)

### Curriculum updates

When a university updates a course description:
- A new `CurriculumVersion` is created
- The old courses remain in storage with their old `curriculum_version_id`
- A new skill extraction run is triggered for the updated program
- A new `AlignmentRun` is created referencing the new curriculum version

---

## Multi-university design

All tables carry `university_id`. Filtering is done at the query layer, not by file separation.

For Phase 1 MVP: filter to `university_id = YSU` in the data loader. No other code changes needed.

For Phase 2: add login → each session carries a `university_id` context → queries filter accordingly.

For multi-tenant SaaS: organization-level isolation is enforced at the API layer; the underlying data model is unchanged.

---

## File structure conventions (Phase 1 MVP)

```
data/
  raw/
    jobs/[source]/             ← raw scraped files, named by source
    university/[uni]/          ← raw curriculum files
    esco/                      ← ESCO taxonomy files
  processed/
    curriculum/                ← cleaned course data
    jobs/                      ← cleaned and filtered job data
    unified/                   ← alignment results and skill data
    role_aware/                ← role mapping and role-split analysis
    esco/                      ← ESCO embeddings and calibration
    llm_skills/                ← LLM-based extraction outputs
  runs/
    [run_id]/                  ← per-run output storage (Phase 3+)
      alignment_results.csv
      gap_analysis.csv
      metadata.json
```

For Phase 1, `runs/` does not exist yet. A stub `metadata.json` should be created at `data/runs/march_2026_static/metadata.json` to record the provenance of the current data, so the product can show an honest data freshness statement.

---

## Stub metadata for March 2026 snapshot

Create this file: `data/runs/march_2026_static/metadata.json`

```json
{
  "run_id": "march_2026_static",
  "is_canonical": true,
  "experiment": "LLM_desc_semantic",
  "created_at": "2026-03-21",
  "curriculum_snapshot": {
    "collected_at": "2026-03-20",
    "n_universities": 8,
    "n_programs": 44,
    "n_courses": 1545
  },
  "job_snapshot": {
    "collected_at": "2026-03-20",
    "n_it_postings": 753,
    "n_sources": 13,
    "window": "static"
  },
  "esco_version": "v1.2",
  "notes": "Thesis research snapshot. Static. Not refreshed after March 2026."
}
```

This file is what the Admin page reads to show data freshness for the MVP.
