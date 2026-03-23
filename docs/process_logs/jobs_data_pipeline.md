# Jobs Data Pipeline

*Dataset: `data/processed/jobs/final_jobs_dataset.csv`*
*Phase 2 — Jobs side | Last updated: 2026-03-22*
*Purpose: Produce a clean, analysis-ready jobs dataset for the curriculum–job-market alignment study.*

---

## 1. Overview

Job posting data is collected from **11 sources** across two categories:

| Category | Sources | Rows |
|---|---|---|
| **Aggregators** (broad Armenia IT market) | LinkedIn, Staff.am, job.am | 1,067 |
| **Company portals** (large Armenian IT employers) | EPAM, SoftConstruct, Krisp, DataArt, ServiceTitan, Synopsys, Picsart, DISQO | 281 |
| **Total** | 11 sources | **1,348** |

All sources are cleaned and standardized to a shared canonical schema, then merged into `final_jobs_dataset.csv`.

The `source_type` column distinguishes aggregators (broad market signal) from company portals (employer-specific signal), enabling weighted analysis in Phase 4.

---

## 2. Canonical Schema (13 columns)

| Column | Type | Notes |
|---|---|---|
| `source` | string | Source identifier (e.g., "linkedin", "epam") |
| `source_type` | string | `"aggregator"` or `"company_portal"` |
| `source_url` | string | Direct URL to the job posting |
| `job_title` | string | Job title as posted |
| `company_name` | string | Hiring company |
| `location` | string | Location string as scraped |
| `employment_type` | string | Full-time / Part-time / Contract / Intern |
| `seniority_level` | string | Junior / Mid / Senior / Lead / Internship |
| `industries` | string | Industry sector(s) |
| `posting_date` | string | `YYYY-MM-DD` format |
| `deadline` | string | `YYYY-MM-DD` format (mostly blank) |
| `skills_tags` | string | Structured skill tags where available |
| `full_text` | string | Full job description text — **primary NLP field** |

**Field coverage in final merged dataset:**

| Field | Coverage |
|---|---|
| source, source_url, job_title, company_name, location, full_text | 100% |
| employment_type | 80% |
| seniority_level | 88% |
| industries | 90% |
| posting_date | 86% |
| skills_tags | 12% (Staff.am + EPAM only) |
| deadline | 6% (Staff.am + Synopsys only) |

---

## 3. Sources

### 3.1 LinkedIn (`source_type: aggregator`)
- **Rows:** 992
- **Method:** Apify LinkedIn Jobs Scraper (cloud-based; LinkedIn blocks direct scraping)
- **Collected:** 2026-03-20 | Search: Armenian IT job market
- **Raw file:** `data/raw/jobs/linkedin_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/linkedin_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/01_linkedin_jobs_pipeline.ipynb`
- **Key field:** `descriptionText` (full job description, 100% coverage)
- **Notes:** `seniorityLevel` from LinkedIn taxonomy (94% filled). Includes Armenia-based and remote roles posted to Armenian candidates.

### 3.2 Staff.am (`source_type: aggregator`)
- **Rows:** 55
- **Method:** `requests` + BeautifulSoup; Next.js `__NEXT_DATA__` JSON parsing (listing) + detail page HTML scraping
- **Collected:** 2026-03-22 | Category: Software Development (id=1)
- **Raw file:** `data/raw/jobs/staffam_jobs_raw_v2.csv` (55 non-expired; original v1 at `staffam_jobs_raw.csv`)
- **Standardized:** `data/processed/jobs/staffam_jobs_standardized.csv`
- **Built by:** `scripts/rescrape_staffam.py`
- **Key field:** `full_text` = description + responsibilities + required_qualifications (100% coverage, median 1,755 chars)
- **Notes:** `skills_tags` is a structured field from Staff.am's own taxonomy (98% filled). Armenia-specific board; 4 expired listings excluded.

### 3.3 job.am (`source_type: aggregator`)
- **Rows:** 20
- **Method:** `requests` + BeautifulSoup (standard SSR HTML)
- **Collected:** 2026-03-22 | IT category (I=17) + keyword searches
- **Raw file:** `data/raw/jobs/jobam_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/jobam_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/03_jobam_scraping.ipynb`
- **Notes:** job.am has a small IT category (~20 active postings). 21 non-IT jobs filtered out via title/industry keywords. No `posting_date` available.

### 3.4 EPAM (`source_type: company_portal`)
- **Rows:** 108
- **Method:** Internal careers search API (`careers.epam.com/api/jobs/v2/search/careers-i18n`); API discovered via Playwright network interception
- **Collected:** 2026-03-22 | Country filter: Armenia
- **Raw file:** `data/raw/jobs/epam_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/epam_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/07_epam_scraping.ipynb`
- **Notes:** Full content in API response (no detail page scraping needed). Includes `seniority_level` and `skills_tags` from EPAM's taxonomy. Largest company-portal source.

### 3.5 SoftConstruct (`source_type: company_portal`)
- **Rows:** 152
- **Method:** `requests` + BeautifulSoup; PeopleForce platform (SSR HTML), 20-page pagination
- **Collected:** 2026-03-22 | Location filter: Yerevan
- **Raw file:** `data/raw/jobs/softconstruct_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/softconstruct_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/08_softconstruct_scraping.ipynb`
- **Notes:** 196 total jobs → 152 Yerevan-filtered. `seniority_level` inferred from title (41% coverage — many titles lack explicit level indicator).

### 3.6 Krisp (`source_type: company_portal`)
- **Rows:** 7
- **Method:** `requests` + BeautifulSoup (SSR HTML)
- **Collected:** 2026-03-22 | Location filter: Armenia
- **Raw file:** `data/raw/jobs/krisp_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/krisp_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/05_krisp_scraping.ipynb`

### 3.7 DataArt (`source_type: company_portal`)
- **Rows:** 5
- **Method:** `requests` to parse `window.INITIAL_STATE` JSON (listing metadata) + Playwright for full job content (React SPA)
- **Collected:** 2026-03-22 | Location filter: Yerevan
- **Raw file:** `data/raw/jobs/dataart_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/dataart_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/11_dataart_scraping.ipynb`

### 3.8 ServiceTitan (`source_type: company_portal`)
- **Rows:** 4
- **Method:** Workday CXS API (listing) + Playwright headless browser (detail pages — Workday detail API returns HTTP 500)
- **Collected:** 2026-03-22 | Location filter: Yerevan
- **Raw file:** `data/raw/jobs/servicetitan_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/servicetitan_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/06_servicetitan_scraping.ipynb`

### 3.9 Synopsys (`source_type: company_portal`)
- **Rows:** 2
- **Method:** `requests` + BeautifulSoup; Avature ATS (SSR HTML + JSON-LD `JobPosting` structured data)
- **Collected:** 2026-03-22 | Location filter: `?location=Yerevan`
- **Raw file:** `data/raw/jobs/synopsys_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/synopsys_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/10_synopsys_scraping.ipynb`
- **Notes:** Both positions are internships.

### 3.10 Picsart (`source_type: company_portal`)
- **Rows:** 2
- **Method:** Greenhouse public API (`boards-api.greenhouse.io/v1/boards/picsart/jobs?content=true`)
- **Collected:** 2026-03-22 | Location filter: Armenia
- **Raw file:** `data/raw/jobs/picsart_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/picsart_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/04_picsart_scraping.ipynb`

### 3.11 DISQO (`source_type: company_portal`)
- **Rows:** 1
- **Method:** Lever public API (`api.lever.co/v0/postings/disqo?mode=json`)
- **Collected:** 2026-03-22 | Location filter: Armenia
- **Raw file:** `data/raw/jobs/disqo_jobs_raw.csv`
- **Standardized:** `data/processed/jobs/disqo_jobs_standardized.csv`
- **Built by:** `notebooks/jobs/09_disqo_scraping.ipynb`

---

## 4. Merge

**Script:** `scripts/merge_jobs.py`
**Output:** `data/processed/jobs/final_jobs_dataset.csv` — 1,348 rows, 13 columns

Each source is normalized to the canonical schema (see Section 2). Where a field is absent from a source's standardized file, it is left blank. `seniority_level` is derived from the job title when not available in structured form.

---

## 5. What This Dataset Does Not Contain

- **Salary data** — not reliably available from any source at scale
- **Applicant counts or engagement metrics**
- **Historical data** — all sources are point-in-time snapshots (March 2026)
- **Complete Armenia IT market coverage** — LinkedIn may include remote roles; several large companies (NPUA, Picsart engineering, etc.) had limited or no postings at collection time
- **Skills tags at scale** — structured tags available only for Staff.am (98%) and EPAM (~60%); extracted programmatically in Phase 3

---

## 6. Notes for Phase 3 (NLP)

- Primary NLP field: **`full_text`** (100% coverage, 141–15,594 chars, median 2,879)
- The `source_type` column can be used to apply differential weights in analysis: company portal postings reflect direct employer demand; aggregator postings reflect the broader market
- `skills_tags` from Staff.am and EPAM can serve as a validation set for NLP-extracted skills
- YSU course names in `final_curriculum_dataset.csv` are in Armenian — translation or multilingual embeddings needed before cross-dataset comparison

---

*For scraping technical details, see `docs/scraping_methods_log.md`.*
*For curriculum data pipeline, see `docs/data_processing_pipeline.md`.*
