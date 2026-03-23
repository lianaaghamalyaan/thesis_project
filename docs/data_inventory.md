# Data Inventory

*Last updated: 2026-03-23 — All analysis phases complete. Thesis writing in progress.*

## Project Structure

```
data/
├── raw/                              <- original data, NEVER modified
│   ├── university/
│   │   ├── reference_curriculum.csv      manually collected, all 4 universities
│   │   └── apify/
│   │       ├── ysu_batch1_2026-03-20.json    14 YSU pages (batch 1)
│   │       ├── ysu_batch2_2026-03-21.json     8 YSU pages (batch 2)
│   │       ├── ysu_merged.json            <- canonical YSU: 22 pages combined
│   │       ├── nuaca_programs_2026-03-21.json  5 NUACA pages
│   │       ├── aua_courses_2026-03-21.json     AUA full course catalog (1 page)
│   │       └── aua_overview_2026-03-21.json   4 AUA overview pages (superseded)
│   ├── jobs/
│   │   ├── linkedin_jobs_raw.csv             992 LinkedIn job postings
│   │   ├── linkedin_jobs_armenia_2026-03-20.csv   original Apify export (preserved)
│   │   ├── staffam_listings_raw.json         Staff.am __NEXT_DATA__ payloads, 2 pages
│   │   ├── staffam_jobs_raw.csv             58 Staff.am IT jobs (original scrape)
│   │   ├── staffam_jobs_raw_v2.csv          55 Staff.am IT jobs (re-scrape, full content)
│   │   ├── jobam_jobs_raw.csv               20 job.am IT jobs
│   │   ├── picsart_jobs_raw.csv              2 Picsart Armenia jobs
│   │   ├── krisp_jobs_raw.csv                7 Krisp Armenia jobs
│   │   ├── servicetitan_jobs_raw.csv         4 ServiceTitan Yerevan jobs
│   │   ├── epam_jobs_raw.csv               108 EPAM Armenia jobs
│   │   ├── softconstruct_jobs_raw.csv       152 SoftConstruct Yerevan jobs
│   │   └── disqo_jobs_raw.csv                1 DISQO Armenia job
│   └── _originals/                   <- raw Apify export filenames + duplicates
│
├── processed/
│   ├── university/
│   │   ├── ysu_courses_parsed.csv        820 courses — YSU, IT programs only, with program_name
│   │   ├── nuaca_courses_parsed.csv      174 courses — NUACA
│   │   ├── aua_courses_parsed.csv        249 courses — AUA
│   │   ├── rau_courses_parsed.csv         47 courses — RAU (1 program)
│   │   ├── _archive_unified_curriculum.csv  1,290 rows — intermediate (superseded, do not use)
│   │   ├── final_curriculum_dataset.csv  *** 1,161 rows — FINAL THESIS ANALYSIS DATASET ***
│   │   ├── ysu_translated.csv            1,161 rows — NLP input with English translations
│   │   ├── translation_cache.json        OpenAI API response cache (keyed by MD5 hash)
│   │   ├── translation_comparison_50.csv 50-row OpenAI vs Perplexity quality evaluation
│   │   └── missing_programs.csv          identified gaps: RAU partial, NPUA 403, UFAR unassessed
│   └── jobs/
│       ├── linkedin_jobs_standardized.csv       992 rows — LinkedIn (source schema)
│       ├── staffam_jobs_standardized.csv         55 rows — Staff.am (source schema)
│       ├── jobam_jobs_standardized.csv           20 rows — job.am (source schema)
│       ├── picsart_jobs_standardized.csv          2 rows — Picsart (canonical schema)
│       ├── krisp_jobs_standardized.csv            7 rows — Krisp (canonical schema)
│       ├── servicetitan_jobs_standardized.csv     4 rows — ServiceTitan (canonical schema)
│       ├── epam_jobs_standardized.csv           108 rows — EPAM (canonical schema)
│       ├── softconstruct_jobs_standardized.csv  152 rows — SoftConstruct (canonical schema)
│       ├── disqo_jobs_standardized.csv            1 row  — DISQO (canonical schema)
│       ├── synopsys_jobs_standardized.csv         2 rows — Synopsys (canonical schema)
│       ├── dataart_jobs_standardized.csv          5 rows — DataArt (canonical schema)
│       └── final_jobs_dataset.csv            *** 1,348 rows — FINAL JOBS DATASET ***
│
│
├── processed/esco/                   ESCO normalization outputs (Phases 4–5)
│   ├── esco_embeddings.npy           pre-computed ESCO label embeddings (13,937 × 384)
│   ├── esco_embedding_ids.csv        ESCO URI + preferred label index
│   ├── calibration_pairs.csv         293 annotated phrase–concept pairs (threshold calibration)
│   ├── threshold_metrics.csv         P/R/F1 at each threshold (0.60–0.85)
│   ├── threshold_calibration_plot.png  F1 curve visualization
│   ├── phrase_to_esco.csv            all 19,998 phrases → best ESCO match (uri, label, sim, matched)
│   ├── tfidf_curriculum_esco_mapped.json   per-course ESCO concept lists + unmatched phrases
│   ├── tfidf_jobs_esco_mapped.json         per-job ESCO concept lists + unmatched phrases
│   ├── keybert_curriculum_esco_mapped.json
│   ├── keybert_jobs_esco_mapped.json
│   ├── alignment_normalized.json     overlap/gap/surplus at ESCO concept level (both methods)
│   ├── alignment_per_program.csv     per-program ESCO coverage (25 programs × 2 methods)
│   ├── alignment_by_university.csv   university-level aggregation
│   ├── alignment_by_degree.csv       Bachelor vs. Master comparison
│   ├── gap_analysis.csv              top gap skills ranked by job market frequency
│   └── emerging_tech_skills.csv      modern tools beyond ESCO (lexicon-matched, 24 terms)
│
docs/figures/                         publication-ready charts
│   ├── per_program_coverage.png      horizontal bar chart, all 25 programs, color-coded by university
│   └── gap_surplus_breakdown.png     top 20 gap and surplus skills side-by-side
│
docs/
│   ├── methodology_walkthrough.md    full pipeline explanation with results
│   ├── skill_extraction_results.md   pre-ESCO extraction details and baseline
│   ├── sensitivity_analysis.md       robustness checks (description asymmetry, validation, noise)
│   ├── esco_calibration_results.md   threshold calibration detail
│   ├── translation_decision.md       OpenAI vs. Perplexity comparison rationale
│   ├── data_gaps_and_limitations.md  university coverage constraints
│   ├── project_overview.md           high-level project summary and pipeline state
│   └── thesis/                       chapter drafts (Chapters 1–7 + abstract)
```

---

## Raw Data — University

### `reference_curriculum.csv`
1,143 courses | 4 universities (YSU, AUA, RAU, NUACA) | 23 programs | Manually collected
Used for: YSU program name correction (URL-based mapping), cross-validation

### `apify/ysu_merged.json` (canonical YSU source)
22 pages | Faculties 78, 85, 516, 520, 525 | Markdown tables with Armenian course names
3 pages returned 404 (programs 310, 311, 354 — inactive)

### `apify/nuaca_programs_2026-03-21.json`
5 pages | All NUACA IT/STEM programs | Plain-text course listings, English names

### `apify/aua_courses_2026-03-21.json`
1 page (full catalog) | 7 programs | Structured fields: code, title, description, credits, prerequisites

### `apify/aua_overview_2026-03-21.json`
4 pages | Program overviews only, no course data | Superseded by `aua_courses_2026-03-21.json`

---

## Raw Data — Jobs

### `linkedin_jobs_raw.csv` (renamed from `linkedin_jobs_armenia_2026-03-20.csv`)
992 postings | Armenia | Key fields: `title`, `descriptionText`, `seniorityLevel`, `industries`
Original file preserved at `data/raw/jobs/linkedin_jobs_armenia_2026-03-20.csv`

### `staffam_listings_raw.json`
2 listing pages | 62 job cards | Full `__NEXT_DATA__` payloads for reproducibility
Scraped: 2026-03-22 | Category: Software Development (id=1) | `totalCount=58` (site-reported)

### `jobam_jobs_raw.csv`
20 rows | 15 columns | IT jobs from job.am (category I=17 + keyword filtering)
Scraped: 2026-03-22 | 0 errors | 100% full_text coverage
Built by: `notebooks/jobs/03_jobam_scraping.ipynb`

### `staffam_jobs_raw.csv`
58 rows | 11 columns | Original scrape (description only — superseded)
Scraped: 2026-03-22 | Fields: `source, source_url, job_title, company_name, location, posting_date, deadline_date, employment_type, specialist_level, description, jsonld_raw`

### `staffam_jobs_raw_v2.csv`
55 rows | 18 columns | Improved re-scrape with full content (non-expired only)
Scraped: 2026-03-22 | 0 errors | 100% field coverage
Fields: `source, source_url, job_title, company_name, location, is_remote, employment_type, specialist_level, posting_date, deadline, salary_from, salary_to, salary_currency, skills_tags, description, responsibilities, required_qualifications, full_text`
Built by: `scripts/rescrape_staffam.py`

### `picsart_jobs_raw.csv`
2 rows | Armenia-filtered | Picsart careers (Greenhouse ATS)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/04_picsart_scraping.ipynb`

### `krisp_jobs_raw.csv`
7 rows | Armenia-filtered | Krisp careers (SSR HTML)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/05_krisp_scraping.ipynb`

### `servicetitan_jobs_raw.csv`
4 rows | Yerevan-filtered | ServiceTitan careers (Workday + Playwright)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/06_servicetitan_scraping.ipynb`

### `epam_jobs_raw.csv`
108 rows | Armenia-filtered | EPAM careers (internal search API)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/07_epam_scraping.ipynb`

### `softconstruct_jobs_raw.csv`
152 rows | Yerevan-filtered | SoftConstruct careers (PeopleForce SSR HTML)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/08_softconstruct_scraping.ipynb`

### `disqo_jobs_raw.csv`
1 row | Armenia-filtered | DISQO careers (Lever public API)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/09_disqo_scraping.ipynb`

### `synopsys_jobs_raw.csv`
2 rows | Yerevan-filtered | Synopsys careers (Avature SSR HTML + JSON-LD)
Scraped: 2026-03-22 | Built by: `notebooks/jobs/10_synopsys_scraping.ipynb`

---

## Processed Data — Jobs

### `linkedin_jobs_standardized.csv` — 992 rows
Built by: `notebooks/jobs/01_linkedin_jobs_pipeline.ipynb`
13 columns: `id, title, standardizedTitle, companyName, location, employmentType, seniorityLevel, jobFunction, industries, postedAt, descriptionText, link, applyUrl`
Primary NLP field: `descriptionText` (100% filled)

### `staffam_jobs_standardized.csv` — 55 rows (updated 2026-03-22)
Built by: `scripts/rescrape_staffam.py` (re-scrape with full content)
18 columns: `source, source_url, job_title, company_name, location, is_remote, employment_type, specialist_level, posting_date, deadline, salary_from, salary_to, salary_currency, skills_tags, description, responsibilities, required_qualifications, full_text`
Field coverage: 100% on all fields
**Primary NLP field: `full_text`** (description + responsibilities + required_qualifications concatenated, min 502 / median 1755 / max 3401 chars)
`skills_tags`: comma-separated structured skill tags from Staff.am taxonomy (98% filled)

### `jobam_jobs_standardized.csv` — 20 rows (created 2026-03-22)
Built by: `notebooks/jobs/03_jobam_scraping.ipynb`
14 columns: `source, source_url, job_title, company_name, location, employment_type, experience_level, salary, deadline, description, responsibilities, requirements, additional_notes, full_text`
100% full_text coverage | full_text median 1624 chars | 21 non-IT jobs filtered out
Note: job.am has a small IT category (20 active postings); all are included

### `picsart_jobs_standardized.csv` — 2 rows (created 2026-03-22)
Built by: `notebooks/jobs/04_picsart_scraping.ipynb` | Greenhouse API, Armenia filter
Canonical schema: `source, source_url, job_title, company_name, location, employment_type, seniority_level, department, posting_date, deadline, skills_tags, full_text`

### `krisp_jobs_standardized.csv` — 7 rows (created 2026-03-22)
Built by: `notebooks/jobs/05_krisp_scraping.ipynb` | requests+BS4, Armenia filter
full_text median 3694 chars

### `servicetitan_jobs_standardized.csv` — 4 rows (created 2026-03-22)
Built by: `notebooks/jobs/06_servicetitan_scraping.ipynb` | Workday API listing + Playwright detail, Yerevan filter
full_text range 4959–8158 chars

### `epam_jobs_standardized.csv` — 108 rows (created 2026-03-22)
Built by: `notebooks/jobs/07_epam_scraping.ipynb` | EPAM internal search API, Armenia country filter
Includes: `seniority_level`, `skills_tags`, `department` fields | full_text 100% coverage

### `softconstruct_jobs_standardized.csv` — 152 rows (created 2026-03-22)
Built by: `notebooks/jobs/08_softconstruct_scraping.ipynb` | PeopleForce SSR HTML (20 listing pages), Yerevan filter
full_text median 2202 chars

### `disqo_jobs_standardized.csv` — 1 row (created 2026-03-22)
Built by: `notebooks/jobs/09_disqo_scraping.ipynb` | Lever public API, Armenia filter
full_text 6721 chars

### `synopsys_jobs_standardized.csv` — 2 rows (created 2026-03-22)
Built by: `notebooks/jobs/10_synopsys_scraping.ipynb` | Avature SSR + JSON-LD, Yerevan filter
Both internship positions | includes `industries`, `deadline` fields

### `final_jobs_dataset.csv` — **1,068 rows ★ FINAL JOBS DATASET (deduplicated) ★**
Built by: `scripts/merge_jobs.py` + `notebooks/jobs/12_jobs_deduplication.ipynb` | All 11 sources merged, 280 duplicates removed
Schema (13 columns): `source, source_type, source_url, job_title, company_name, location, employment_type, seniority_level, industries, posting_date, deadline, skills_tags, full_text`

**Pre-dedup:** 1,348 rows from 11 sources. **Post-dedup:** 1,068 rows (280 removed by `notebooks/jobs/12_jobs_deduplication.ipynb` — 75 within-source, 205 cross-source duplicates).

| Source | Post-dedup rows |
|---|---|
| linkedin | 734 |
| softconstruct | 141 |
| epam | 104 |
| staff.am | 48 |
| job.am | 20 |
| krisp | 7 |
| dataart | 5 |
| servicetitan | 4 |
| picsart | 2 |
| synopsys | 2 |
| disqo | 1 |
| **Total** | **1,068** |

full_text: 100% coverage, 0 nulls, 0 empty.
See `docs/jobs_data_pipeline.md` Section 4 for the canonical column mapping.

---

## Processed Data — University

### `ysu_courses_parsed.csv` — 820 courses (IT programs only)
562 Bachelor, 258 Master | 13 programs | Columns: source_url, degree_type, speciality, program_name, academic_year, component, chair_code, course_name_original, credits
Note: Non-IT programs (Finance, Management, Economics) filtered out. Program names corrected from official speciality codes to actual program names via URL mapping.

### `nuaca_courses_parsed.csv` — 174 courses
118 Bachelor, 56 Master | 4 programs | Columns: source_url, university, program_name, degree_type, semester, module_code, course_name, credits, assessment

### `aua_courses_parsed.csv` — 249 courses
136 Bachelor, 86 Master, 27 General Education | 7 programs | Columns: program, course_code, title, description, credits, prerequisites, corequisites, university, program_name, degree_type

### `rau_courses_parsed.csv` — 47 courses
All Bachelor | 1 program (Applied Mathematics and Informatics 01.03.02) | Columns: university, program_name, degree_type, course_code, course_name_russian, course_name_english, credits, component, source
Source: PDF study plans (rau.am/sveden/education/programs/)

### `unified_curriculum.csv` — 1,290 rows (intermediate — superseded)
Produced by `merge_unified_curriculum.py`. Contains all 4 universities before deduplication.
**Do not use for analysis — use `final_curriculum_dataset.csv` instead.**

### `final_curriculum_dataset.csv` — 1,161 rows ★ FINAL DATASET ★
Produced by `build_final_curriculum.py`. See `docs/data_processing_pipeline.md` for full details.

| University | Rows | Programs |
|---|---|---|
| Yerevan State University | 691 | 13 |
| American University of Armenia | 249 | 7 |
| National University of Architecture and Construction of Armenia | 174 | 4 |
| Russian-Armenian University | 47 | 1 |
| **Total** | **1,161** | **25** |

**Schema (18 columns):**
`course_id, university, program_name, program_code, degree_level, course_code, course_name, course_name_original, credits, component, semester, description, prerequisites, assessment, academic_year, source_url, source_language, notes`

**Key properties:**
- `course_name`: Armenian for YSU, English for AUA/NUACA, English (translated) for RAU
- `course_name_original`: Russian original for RAU; blank for others
- `description`: AUA (249 rows) + YSU (691 rows) = 940 rows total
- `prerequisites`: populated for AUA only (119/249 rows)
- `semester`: NUACA + YSU (691 rows, integer 1-8)
- `component`: populated for YSU and RAU; blank for AUA and NUACA
- `assessment`: NUACA (Exam/Test) + YSU (Exam/Attestation/Defense, 691/691 = 100%)
- 8 rows carry data-quality flags in `notes` column

### `missing_programs.csv` — 10 entries (identified gaps)
| Institution | Status | Programs | Count |
|---|---|---|---|
| RAU | Partial — PDFs accessible | Additional IT programs not parsed | 7 |
| NPUA | Excluded — HTTP 403 | ~10 IT programs | 1 row (summary) |
| UFAR | Excluded — not assessed | Unknown IT programs | 1 row |
| YSU | Inactive pages | 3 programs (404) | 1 row |

### `ysu_translated.csv` — 1,161 rows ★ NLP INPUT ★
Extension of `final_curriculum_dataset.csv` with two additional columns produced by OpenAI gpt-4o-mini translation:
- `course_name_en`: English course name (all 1,161 rows — passthrough for AUA/NUACA, translated for YSU, pre-translated for RAU)
- `description_en`: English description (933/1,161 rows — where description exists)
Used as the primary input for skill extraction (Phase 3).

---

## Processed Data — Skills (`data/processed/skills/`)

All files produced by `notebooks/03_skill_extraction.ipynb` (2026-03-23).
Sensitivity analysis: `notebooks/03b_sensitivity_analysis.ipynb` (description asymmetry, skills_tags validation, noise audit).

### `tfidf_curriculum_skills.json`
TF-IDF top-10 keywords per curriculum document. Keys = `course_id`. Values = `[(keyword, tfidf_score), ...]`.
Corpus: 1,161 curriculum documents. Vectorizer: ngram_range=(1,3), max_df=0.85, min_df=2, combined stopwords.

### `tfidf_jobs_skills.json`
TF-IDF top-10 keywords per job posting. Keys = row index. Values = `[(keyword, tfidf_score), ...]`.
Corpus: 1,068 job postings (after 140 boilerplate paragraphs removed).

### `keybert_curriculum_skills.json`
KeyBERT top-10 keyphrases per curriculum document (all-MiniLM-L6-v2, use_mmr=True, diversity=0.5).

### `keybert_jobs_skills.json`
KeyBERT top-10 keyphrases per job posting (all-MiniLM-L6-v2, use_mmr=True, diversity=0.5).

### `method_comparison.csv`
Side-by-side alignment metrics for TF-IDF vs KeyBERT: coverage rate, Jaccard, overlap count, gap count, surplus count.

### `alignment_details.json`
Full overlap/gap/surplus skill lists for both methods. Large file (~1 MB) — used for Phase 4 analysis.

---

## Documentation

### `docs/data_collection_log.md`
Technical log of all scraping runs, file formats, parsing methods, known issues.
Use for thesis Chapter 3 (Methodology).

### `docs/data_gaps_and_limitations.md`
Formal inventory of universities with partial/no data (RAU, NPUA, UFAR).
Includes ready-to-use thesis paragraph. Use for thesis Chapter 3/4.

### `docs/data_processing_pipeline.md`
Schema decisions, cleaning log, harmonisation rationale, intentional non-cleaning decisions.
Use for thesis Chapter 3 (Data Description / Processing).

### `docs/scraping_methods_log.md`
Per-source technical decisions: which HTTP method, which ATS platform, why Playwright vs requests, key code patterns, robots.txt compliance.
Use for thesis Chapter 3 (Methodology / Data Collection).

### `docs/sensitivity_analysis.md`
Sensitivity analysis of the NLP extraction pipeline: description asymmetry (AUA test, 5x coverage difference), validation against skills_tags (151 jobs, TF-IDF 44% recall), noise audit (60% of overlap was generic English). Companion to `notebooks/03b_sensitivity_analysis.ipynb`.
Use for thesis Chapter 4 (Section 4.5.7).

---

## Archived
`data/raw/_originals/` — raw Apify export filenames and duplicates. Safety backup, not used by any pipeline.
