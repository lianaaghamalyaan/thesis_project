# Methodology Walkthrough — From Raw Data to Alignment Results

*A step-by-step explanation of the full pipeline with real examples from the data.*

---

## Overview

This thesis measures how well Armenian IT university curricula match employer skill demands. The pipeline has 5 stages:

```
RAW DATA → CLEANING → SKILL EXTRACTION → ESCO NORMALIZATION → ALIGNMENT ANALYSIS
```

Each stage is explained below with real inputs and outputs.

---

## Stage 1: Raw Data Collection

### What was collected

**Curriculum side:** Course information from 4 Armenian universities.
- **YSU** (691 courses, 13 programs) — scraped via Apify from ysu.am, Armenian language
- **AUA** (249 courses, 7 programs) — scraped from aua.am course catalog, English, with full descriptions
- **NUACA** (174 courses, 4 programs) — scraped from nuaca.am, English course names
- **RAU** (47 courses, 1 program) — parsed from PDF study plans, Russian → English

**Job market side:** IT job postings from 11 sources.
- 3 aggregators: LinkedIn (734), Staff.am (48), job.am (20)
- 8 company portals: EPAM (104), SoftConstruct (141), Krisp (7), DataArt (5), ServiceTitan (4), Synopsys (2), Picsart (2), DISQO (1)

### Real example — raw curriculum data

| Field | Value |
|---|---|
| University | Yerevan State University |
| Program | Data Science in Business |
| Course (Armenian) | Տdelays ադdelays (Python) |
| Course (English, translated) | Information Technologies in the Professional Field (Python) |
| Description | Application of the fundamentals of the Python programming language, working with data, variables, arrays, functions... |

### Real example — raw job posting

| Field | Value |
|---|---|
| Source | LinkedIn |
| Company | Align Technology |
| Title | Senior Program Manager |
| Text preview | "Join a team that is changing millions of lives. Transforming smiles..." |

---

## Stage 2: Data Cleaning & Structuring

### What was done

1. **Curriculum:** Merged all 4 universities into a unified 18-column schema (`final_curriculum_dataset.csv`, 1,161 rows). Removed 129 YSU within-program duplicates. Normalized assessment values.

2. **Jobs:** Merged all 11 sources into a 13-column schema (`final_jobs_dataset.csv`). Removed 280 duplicates (75 within-source, 205 cross-source). Final: **1,068 unique job postings**.

3. **Translation:** Translated 691 YSU course names and descriptions from Armenian to English using OpenAI gpt-4o-mini. Quality validated: 20/20 vs Perplexity 6/20.

### Output files

| File | Rows | Purpose |
|---|---|---|
| `data/processed/university/final_curriculum_dataset.csv` | 1,161 | Canonical curriculum data |
| `data/processed/university/ysu_translated.csv` | 1,161 | NLP-ready version with English text |
| `data/processed/jobs/final_jobs_dataset.csv` | 1,068 | Canonical job postings |

---

## Stage 3: Skill Extraction (NLP)

### What this stage does

Extracts skill-related keywords from each document using two unsupervised methods.

### How TF-IDF works

TF-IDF (Term Frequency–Inverse Document Frequency) identifies words that are statistically distinctive in a document relative to the whole corpus. Common words like "the" or "students" get low scores. Distinctive terms like "python" or "cloud" get high scores.

**Configuration:** ngram_range=(1,3), max_df=0.85, min_df=2, English + 200 custom stopwords.

### How KeyBERT works

KeyBERT uses a pre-trained BERT model (`all-MiniLM-L6-v2`, 22M parameters) to find phrases most semantically similar to the document as a whole. It "reads" the meaning, not just word frequency.

**Configuration:** top_n=10, use_mmr=True (diversity=0.5) to avoid repetitive phrases.

### Preprocessing applied before extraction

| Step | Purpose | Example |
|---|---|---|
| Boilerplate removal | 140 recurring paragraphs stripped from jobs | EPAM "About Us" section appearing in 100+ postings |
| Custom stopwords (295) | Remove academic/job filler | `familiarize`, `introduce`, `semester`, `seeking`, `candidate`, `yerevan` |
| Company name filter | Block 434 company name tokens as false skills | `softconstruct`, `epam`, `krisp` |
| Generic unigram filter (459) | Remove common English words that are not skills | `access`, `achieve`, `activities`, `challenges`, `efficiency` |
| `is_skill_like()` post-filter | Reject generics, noise phrases, all-stop n-grams | Removes pure numbers, single-letter tokens, multi-word noise |

### Real extraction example — curriculum

**Course:** "Information Technologies in the Professional Field (Python)" (YSU, Data Science)

| Method | Top-5 extracted skills |
|---|---|
| TF-IDF | `python`, `data`, `language data variables`, `arrays functions`, `language data` |
| KeyBERT | `data visualization python`, `visualization python teaching`, `fundamentals python`, `python teaching`, `teaching create visualizations` |

**Observation:** TF-IDF extracts individual words (`python`, `data`). KeyBERT extracts meaningful phrases (`data visualization python`). Both capture the course's core content, but in different forms.

### Real extraction example — job posting

**Job:** "Senior Program Manager" (Align Technology, LinkedIn)

| Method | Top-5 extracted skills |
|---|---|
| TF-IDF | `program`, `lives transforming`, `transforming`, `matrixed`, `invisalign` |
| KeyBERT | `process improvement projects`, `orthodontic industry introduction`, `emea armenia yerevan`, `oversee multiple transformational`, `root cause analysis` |

### Raw alignment results (pre-ESCO, after noise cleanup)

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Curriculum unique skills | 3,423 | 4,801 |
| Job market unique skills | 4,625 | 8,695 |
| **Overlap** | **296 (6.4%)** | **23 (0.26%)** |
| Gap (jobs need, curriculum doesn't teach) | 4,329 | 8,672 |
| Surplus (curriculum teaches, jobs don't ask) | 3,127 | 4,778 |

### Why KeyBERT overlap is so low (and why that's OK)

TF-IDF extracts single words that naturally match across corpora — `data` appears in both curriculum and job descriptions. KeyBERT extracts multi-word phrases that are idiomatic to each corpus:
- Curriculum: `"object oriented programming"`, `"mathematical modeling applications"`
- Jobs: `"backend development experience"`, `"cloud infrastructure design"`

These phrases describe overlapping skills but don't match as strings. **ESCO normalization (Stage 4) solves this** by mapping both to shared ESCO concept IDs.

### Examples of overlap, gap, and surplus (TF-IDF)

**Overlap** (taught AND demanded): `algorithms`, `analysis`, `data`, `design`, `machine`, `programming`, `statistics`, `testing`, `cloud`, `agile`

**Gap** (demanded but NOT taught): `abap`, `automation`, `backend`, `ci cd`, `cloud`, `devops`, `docker`, `kubernetes`, `marketing`, `security`

**Surplus** (taught but NOT demanded): `armenian language`, `calculus`, `differential equations`, `french language`, `german`, `history`, `philosophy`, `physics`

---

## Stage 4: ESCO Normalization (next step)

### What ESCO is

ESCO (European Skills, Competences, Qualifications and Occupations) is the EU's standard taxonomy of ~13,939 skill concepts. It provides a shared vocabulary so we can compare extracted phrases that mean the same thing.

### How the mapping works

1. **Encode** all extracted skill phrases AND all ESCO preferred labels using the same sentence embedding model (`all-MiniLM-L6-v2`)
2. **Match** each extracted phrase to its nearest ESCO concept by cosine similarity
3. **Apply threshold** — only keep matches above the calibrated threshold of **0.75** (F1=0.711, empirically confirmed)

### Example of what ESCO normalization does

| Extracted phrase (curriculum) | Extracted phrase (jobs) | Both map to ESCO concept |
|---|---|---|
| `python programming` | `python development` | `Python (programming language)` |
| `machine learning models` | `ML algorithms` | `machine learning` |
| `data analysis` | `data analytics` | `analyse data` |
| `object oriented programming` | `OOP principles` | `object-oriented programming` |

**After normalization:** These pairs, which had zero overlap as raw strings, now count as the same skill.

### The calibration step (Notebooks 04 + 04b)

Before applying ESCO normalization to all 20k+ phrases, the similarity threshold was calibrated empirically:

1. **293 pairs** sampled across 7 similarity bands (0.50–1.00)
2. **Automated annotation** using GPT-4o-mini as judge (temperature=0, binary match/no-match)
3. **Manual validation** of a stratified 35-pair sample — 94.3% agreement (2 corrections applied)
4. **Threshold sweep** across 0.60–0.85, selecting the threshold with best F1

This process is implemented across two notebooks:
- `notebooks/3_analysis/04_esco_calibration.ipynb` — pair generation and threshold sweep
- `notebooks/3_analysis/04b_annotate_calibration_pairs.ipynb` — automated annotation + manual validation

**Status: calibration complete.** Results are in `data/processed/esco/`.

---

## Stage 5: ESCO Normalization — Results

ESCO normalization has been completed. All extracted phrases were encoded with `all-MiniLM-L6-v2` and matched to the nearest ESCO concept by cosine similarity (threshold=0.75).

### Normalized alignment metrics

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum ESCO concepts | 329 | 397 |
| Job market ESCO concepts | 527 | 380 |
| **Overlap** | **133 (25.2%)** | **77 (20.3%)** |
| Gap (demanded, not taught) | 394 | 303 |
| Surplus (taught, not demanded) | 196 | 320 |

Coverage improved dramatically versus the pre-ESCO string-level baseline (TF-IDF: 6.4% → 25.2%; KeyBERT: 0.26% → 20.3%), confirming that ESCO normalization collapses surface-form variation into shared concept IDs.

### Knowledge vs. competence split

ESCO classifies each concept as *knowledge* or *skill/competence*. The overlap is 70% knowledge, 30% competence. The gap is 51% applied competences. This means curricula cover the right subject domains but fall short on applied practice — DevOps pipelines, CI/CD, cloud deployment, responsive design.

### Sample overlap (taught AND demanded)
`algorithms`, `Python`, `SQL`, `JavaScript`, `NoSQL`, `Agile development`, `blockchain`, `Internet of Things`, `automation technology`, `architectural design`

### Sample gap (demanded, NOT taught)
`Java`, `PHP`, `MySQL`, `PostgreSQL`, `CSS`, `DevOps`, `Android`, `Docker/Ansible`, `Adobe Photoshop`, `GDPR`

### Sample surplus (taught, NOT demanded)
`algebra`, `MATLAB`, `Monte Carlo simulation`, `Assembly`, `Ancient Greek`, `Turkish`, `Chinese`

### Per-program coverage (TF-IDF, top programs)

| University | Program | Degree | Coverage |
|---|---|---|---:|
| AUA | Computer and Information Science | Master | 9.1% |
| AUA | Computer Science | Bachelor | 7.2% |
| YSU | Data Science in Business | Master | 5.7% |
| AUA | Data Science | Bachelor | 5.7% |
| NUACA | Informatics (CS) | Bachelor | 2.5% |
| RAU | Applied Mathematics and Informatics | Bachelor | 2.3% |
| NUACA | GIS | Master | 0.6% |

Note: coverage percentages are share of job-market ESCO concepts covered by the program. AUA leads due to richer course descriptions.

---

## Stage 6: Final Alignment Analysis

`06_alignment_analysis.ipynb` — completed. Produces all result tables, charts, and skill frequency analyses.

### Steps 1–10: Alignment metrics, gap/surplus, emerging tech

- Per-program and university-level coverage tables
- Gap analysis: top 50 ESCO concepts demanded by employers but absent from curricula
- Surplus analysis: curriculum content with no job market counterpart
- Emerging tech skills (beyond ESCO v1.2): Docker, Kubernetes, React, TypeScript, AWS, CI/CD, etc., matched via a curated tech lexicon using direct regex search on raw job text

### Step 11: Skill demand by job role

Job postings are classified into 9 IT roles by keyword matching on job title:

| Role | Jobs |
|---|---:|
| Backend | 117 |
| Data / ML / AI | 58 |
| QA / Testing | 48 |
| DevOps / Cloud | 40 |
| Frontend / JS | 34 |
| Full Stack | 26 |
| Security | 14 |
| Hardware / Embedded | 15 |
| Mobile | 8 |

For each role, top 15 skills are computed using **direct text search** on raw job descriptions — not TF-IDF extraction. This avoids the IDF frequency bias that suppresses common terms like Python.

Output: `data/processed/esco/skills_by_role.csv`

### Step 12: Overall skill frequency

Top 60 skills across all IT job postings, combining:
- ESCO concepts: all 760 IT-relevant ESCO concepts (filtered by IT-domain label keywords) searched via `preferredLabel` + `altLabels` regex match on raw text
- Tech lexicon: 30+ modern tools absent from ESCO v1.2, searched directly

ESCO concepts take priority over tech lexicon entries when both cover the same skill (case-insensitive dedup).

**Top 10 most demanded skills (360 IT job postings):**

| Rank | Skill | % of IT jobs |
|---:|---|---:|
| 1 | Python | 35.0% |
| 2 | CI/CD | 30.6% |
| 3 | Amazon Web Services | 27.8% |
| 4 | Docker | 21.1% |
| 5 | Kubernetes | 20.8% |
| 6 | ICT project management methodologies | 19.4% |
| 7 | Microsoft Azure | 19.2% |
| 8 | DevOps | 18.9% |
| 9 | TypeScript | 17.8% |
| 10 | Google Cloud | 17.8% |

Output: `data/processed/esco/skill_frequency_overall.csv`

### Excluded courses

28 courses (2.4% of 1,161) were excluded from skill extraction due to having ≤10 characters of text (name-only entries with no description). These are mostly NUACA general-education courses (Physics, Philosophy, Management, Practice) and RAU general subjects. No IT-relevant courses were lost.

Full list: `data/processed/skills/excluded_courses.csv`

---

## File Map — Where Everything Lives

```
thesis_data/
├── data/
│   ├── raw/                            Original scraped data (never modified)
│   │   ├── university/apify/           Apify JSON exports
│   │   └── jobs/                       Raw CSVs per source
│   ├── processed/
│   │   ├── university/
│   │   │   ├── final_curriculum_dataset.csv    ← 1,161 courses (canonical)
│   │   │   ├── ysu_translated.csv              ← same + English translations (NLP input)
│   │   │   ├── translation_cache.json          ← API response cache (avoids re-running)
│   │   │   └── translation_comparison_50.csv   ← OpenAI vs Perplexity quality evaluation
│   │   ├── jobs/
│   │   │   └── final_jobs_dataset.csv          ← 1,068 jobs (deduplicated)
│   │   └── skills/
│   │       ├── tfidf_curriculum_skills.json    ← TF-IDF keywords per course
│   │       ├── tfidf_jobs_skills.json          ← TF-IDF keywords per job
│   │       ├── keybert_curriculum_skills.json   ← KeyBERT phrases per course
│   │       ├── keybert_jobs_skills.json         ← KeyBERT phrases per job
│   │       ├── method_comparison.csv           ← side-by-side metrics
│   │       ├── alignment_details.json          ← full overlap/gap/surplus lists
│   │       └── excluded_courses.csv            ← 28 courses excluded (≤10 chars text)
│
├── notebooks/
│   ├── 1_collection_jobs/              Per-source scraping notebooks (01–12) + merge (13)
│   ├── 2_collection_university/        University parsing (01), translation (02), build (03), enrich (04)
│   └── 3_analysis/
│       ├── 01_eda.ipynb                Exploratory data analysis (both datasets)
│       ├── 02_skill_extraction.ipynb   TF-IDF + KeyBERT extraction ← HAS OUTPUTS
│       ├── 03_sensitivity_analysis.ipynb  Sensitivity analysis (asymmetry, validation, noise)
│       ├── 04_esco_calibration.ipynb   ESCO pair generation and threshold sweep
│       ├── 04b_annotate_calibration_pairs.ipynb  GPT-4o-mini annotation + manual validation
│       └── 05_esco_normalization.ipynb  Phrase → ESCO mapping, normalized alignment ← HAS OUTPUTS
│
├── docs/
│   ├── methodology_walkthrough.md      ← THIS DOCUMENT
│   ├── skill_extraction_results.md     Phase 3 results summary
│   ├── sensitivity_analysis.md         Sensitivity analysis results (description asymmetry, validation, noise)
│   ├── translation_decision.md         OpenAI vs Perplexity comparison
│   ├── data_collection_log.md          Technical scraping log
│   ├── data_gaps_and_limitations.md    Missing universities, coverage gaps
│   ├── data_processing_pipeline.md     Schema decisions, cleaning rationale
│   ├── jobs_data_pipeline.md           Jobs sources, schemas, merge details
│   └── thesis/                         Thesis chapter drafts (Chapters 1–4)
│
├── DATA_INVENTORY.md                   Complete file inventory with schemas
├── PROJECT_CONTEXT.md                  High-level project summary
└── TASKS.md                            Phase-by-phase task tracker
```

---

## Quick Reference — Key Numbers

| Metric | Value |
|---|---|
| Universities | 4 (YSU, AUA, NUACA, RAU) |
| Programs | 25 |
| Curriculum courses | 1,161 |
| Job postings | 1,068 (from 11 sources, deduplicated) |
| Courses used for NLP | 1,133 (28 too short) |
| TF-IDF unique curriculum skills | 3,423 |
| TF-IDF unique job skills | 4,625 |
| TF-IDF overlap (pre-ESCO) | 296 (6.4%) |
| KeyBERT unique curriculum skills | 4,801 |
| KeyBERT unique job skills | 8,695 |
| KeyBERT overlap (pre-ESCO) | 23 (0.26%) |
| ESCO skill concepts (v1.2) | 13,937 |
| Embedding model | all-MiniLM-L6-v2 (22M params) |
| TF-IDF overlap (post-ESCO) | 133 (25.2% of job-market concepts) |
| KeyBERT overlap (post-ESCO) | 77 (20.3% of job-market concepts) |
| Union overlap (post-ESCO) | 187 (25.7%) |
| ESCO calibration threshold | 0.75 (F1=0.711) |
| Best program coverage | AUA Computer and Information Science, Master — 9.1% |
| Worst program coverage | NUACA Geographic Information Systems, Master — 0.6% |
| Overlap knowledge/competence split | 70% knowledge / 30% competence |
| Courses with 0 ESCO concepts | AUA 12%, YSU 27%, NUACA 48%, RAU 56% |
