# Data Collection & Processing Log

*Use this file when writing Chapter 3 (Methodology) and Chapter 4 (Data Description) of the thesis.*

---

## 1. University Curriculum Data

### 1.1 Reference Dataset (Manual Collection)

**File:** `data/raw/university/reference_curriculum.csv`
**Method:** Manually visited educational plan pages of 4 Armenian universities and recorded course-level information.
**Date:** Prior to 2026-03-20
**Coverage:**

| University | Abbr. | Programs | Courses |
|---|---|---|---|
| Yerevan State University | YSU | 14 | ~680 |
| American University of Armenia | AUA | 4 | ~200 |
| Russian-Armenian University | RAU | 1 | ~60 |
| National Univ. of Architecture and Construction | NUACA | 5 | ~200 |
| **Total** | | **23 programs** | **1,143 courses** |

**Fields collected:** university, program name, degree level (Bachelor/Master), curriculum component (General/Core/Elective), course name in Armenian, course name in English, chair code, credits, hours/week, semester, study year, program duration, course description, source URL.

### 1.2 Automated Scraping — YSU (Apify)

**Tool:** Apify actor `webpage-to-markdown`
**What it does:** Visits a URL and converts the full page content to markdown text.
**Output format:** JSON array, each element = `{url, markdown}`

| Batch | Date | Pages | Programs | File |
|---|---|---|---|---|
| Batch 1 | 2026-03-20 | 14 | Faculty 78 (programs 348–354), Faculty 85 (programs 305–311) | `ysu_batch1_2026-03-20.json` |
| Batch 2 | 2026-03-21 | 8 | Faculty 85 (304), 516 (299, 303, 957), 520 (500, 689), 525 (313, 858) | `ysu_batch2_2026-03-21.json` |
| **Merged** | | **22** | All YSU IT/STEM programs identified in reference | `ysu_merged.json` |

**Parsing:** A Python script (in `notebooks/2_collection_university/01_university_pipeline.ipynb`) extracts structured course data from the markdown using regex:
- Program metadata: degree type, speciality code, academic year
- Course tables: chair code, course name (Armenian), credits
- Curriculum component: matched to `###` section headers

**Result:** `data/processed/university/ysu_courses_parsed.csv` — **1,131 courses** (811 Bachelor, 320 Master)

**Known issues:**
- 3 YSU program pages returned empty content (programs 310, 354, 311) — likely unpublished or placeholder pages on the university website
- Course names are in Armenian only — English translations are available in the reference dataset but not in the scraped data

### 1.3 Automated Scraping — NUACA (Apify)

**Tool:** Apify actor `webpage-to-markdown`
**Date:** 2026-03-21
**File:** `data/raw/university/apify/nuaca_programs_2026-03-21.json`
**Pages scraped:** 5 (all NUACA IT/STEM programs)

**NUACA page format:** Unlike YSU (which uses markdown tables), NUACA pages list courses as plain text lines organized by semester, with format:
```
1 7.20GDS028 Applied Geoinformation Systems (GIS) 4 Exam
```
Each line contains: row number, module code, subject name, credits, and assessment type.

**Parsing:** Custom regex parser that:
- Splits content by semester (identified by `№Educational Module Subject Credits Assessment` headers)
- Extracts module code, course name, credits, and assessment type per line

**Result:** `data/processed/university/nuaca_courses_parsed.csv` — **174 courses**

| Program | Degree | Courses |
|---|---|---|
| Geographic Information Systems | Master | 16 |
| Informatics (Computer Science) | Master | 18 |
| Informatics (Computer Science) | Bachelor | 58 |
| Information Systems | Bachelor | 60 |
| Project Management (in Information Technologies) | Master | 22 |

**Advantage over reference:** Course names in NUACA pages are already in English, and include module codes and semester assignments.

### 1.4 Automated Scraping — AUA (Apify)

**Tool:** Apify actor `webpage-to-markdown`

**Attempt 1 (2026-03-21):** Scraped 4 individual program pages → `aua_overview_2026-03-21.json`
These turned out to be overview/marketing pages with no course data.

**Attempt 2 (2026-03-21):** Scraped `https://cse.aua.am/courses/` → `aua_courses_2026-03-21.json`
This single page contains the complete AUA course catalog — all programs, all courses.

**AUA page format:** Very clean, structured plain text:
```
Program: BSCS
**Course Code: CS100**
**Title: Calculus 1**
Description: This introductory course covers...
Credits: 3.0
Prerequisites: ...
Corequisites: ...
```

**Result:** `data/processed/university/aua_courses_parsed.csv` — **249 courses**

| Program | Degree | Courses |
|---|---|---|
| Computer Science | Bachelor | 44 |
| Data Science | Bachelor | 31 |
| Computer and Information Science | Master | 56 |
| Industrial Engineering and Systems Management | Master | 30 |
| Engineering Sciences | Bachelor | 38 |
| Environmental and Sustainability Sciences | Bachelor | 23 |
| General Education | General | 27 |

**Advantages:** All course names in English, full descriptions for every course, prerequisites listed, course codes included. Richest dataset of all universities.

**Note:** The page includes 3 programs beyond our original 4 reference programs (Engineering Sciences, Environmental Sciences, General Education). These are kept because they share courses with the target programs and are STEM-adjacent.

### 1.5 Automated Scraping — RAU (PDF Study Plans)

**Source:** Official RAU accreditation page at `rau.am/sveden/education/programs/prikladnaya-matematika-i-informatika-01.03.02.html`
**Date:** 2026-03-22
**Method:** Downloaded 4 PDF study plan documents (Years 1–4), extracted text with PyPDF2, parsed with regex.

**Note:** The originally known URL (`impht.rau.am/am/program/bachelor`) was a program overview page with no course listings. A web search in Russian identified the accreditation page which links to downloadable PDF study plans containing the full curriculum.

**RAU PDF format:** Russian-language study plans in tabular PDF format. Each course line contains:
```
+ Б1.О.01 Иностранный язык 123 9 9 324 324 96 228
```
Fields: course code (Russian classification system), course name in Russian, various hour breakdowns and credits.

**Parsing challenges:**
- PDF text extraction concatenates text across page breaks, creating artifacts
- Credit values appear in columns alongside total hours — required pattern matching to identify the correct credit column
- Some entries were duplicated across year boundaries with different formatting

**Result:** `data/processed/university/rau_courses_parsed.csv` — **47 courses**

| Component | Courses |
|---|---|
| Mandatory (Б1.О) | 25 |
| Elective — formative (Б1.В) | 15 |
| Elective — by choice (Б1.В.ДВ) | 7 |

**Post-processing:** English translations added for all 47 course names. 1 course missing credits (Б1.О.09 — Probability Theory and Mathematical Statistics).

### 1.6 Coverage Summary

All 4 universities now have parsed curriculum data:

| University | Programs | Courses | Source | Language |
|---|---|---|---|---|
| YSU | 22 pages | 1,131 | Apify web scrape | Armenian |
| NUACA | 5 programs | 174 | Apify web scrape | English |
| AUA | 7 programs | 249 | Apify web scrape | English |
| RAU | 1 program | 47 | PDF study plans | Russian → English |
| **Total** | | **1,601** | | |

---

## 2. Job Market Data

### 2.1 LinkedIn Job Postings

**Tool:** Apify actor `linkedin-jobs-scraper`
**Date:** 2026-03-20
**File:** `data/raw/jobs/linkedin_jobs_armenia_2026-03-20.csv`

| Metric | Value |
|---|---|
| Total postings | 992 |
| Country | Armenia (100%) |
| Search scope | IT / technology sector |

**Key fields for analysis:**
- `title` — job title (e.g., "Senior Software Engineer")
- `descriptionText` — full job description in plain text (**primary NLP target**)
- `seniorityLevel` — Junior / Mid / Senior / etc.
- `employmentType` — Full-time / Part-time / Contract
- `industries` — industry tags
- `companyName` — employer name

**Status:** Raw data collected. Not yet cleaned or profiled (notebook ready but not run).

---

## 3. Processing Steps Completed

| Step | Input | Output | Method |
|---|---|---|---|
| Parse YSU pages | `ysu_merged.json` (22 pages) | `ysu_courses_parsed.csv` (1,131 rows) | Regex extraction of markdown tables |
| Parse NUACA pages | `nuaca_programs_2026-03-21.json` (5 pages) | `nuaca_courses_parsed.csv` (174 rows) | Regex extraction of plain-text course lines |
| Parse AUA catalog | `aua_courses_2026-03-21.json` (1 page) | `aua_courses_parsed.csv` (249 rows) | Regex extraction of structured fields |
| Parse RAU PDFs | 4 PDF study plans (Years 1–4) | `rau_courses_parsed.csv` (47 rows) | PyPDF2 + regex, manual English translation |
| Compare with reference | parsed CSVs + `reference_curriculum.csv` | `missing_programs.csv` (0 entries) | URL comparison |

---

## 4. Final Data Validation (2026-03-22)

A systematic coverage check was conducted for all universities before freezing the dataset.

### YSU — Confirmed complete
All known IT programs across 5 faculties/institutes verified. Faculty 520 confirmed as the IT Center (hosts 061104 Information Systems Master programs). Three empty pages (programs 310, 311, 354) are no longer listed as active programs on the university's faculty page — treated as inactive.

### AUA — Confirmed complete
`cse.aua.am/courses/` confirmed as the comprehensive course catalog for all programs.

### NUACA — Confirmed complete
All IT-relevant programs in the Faculty of Management and Technology covered. Additional non-IT programs (Economics, Accounting, Logistics, Construction Management) identified and excluded as out of scope.

### RAU — Confirmed partial (gap documented)
6 additional IT-relevant programs identified beyond the existing 01.03.02 bachelor program:
- Bachelor: Infocommunication Technologies and Communication Systems (11.03.02)
- Master: Information Security, Machine Learning, System Programming, Distributed Systems, Infocommunication Technologies
All have downloadable PDF study plans at `impht.rau.am`. Not scraped due to resource constraints. Documented in `docs/data_gaps_and_limitations.md`.

### NPUA (polytech.am) — Inaccessible
All requests to polytech.am return HTTP 403. No course-level data accessible. Documented in `docs/data_gaps_and_limitations.md`.

**Dataset frozen at 1,161 courses. Phase 1 (Data Collection) is complete.**

---

## 5. What Has Not Been Done Yet

- No NLP or skill extraction performed on any dataset
- Job postings not cleaned or deduplicated
- Parsed university datasets not yet merged into one unified file
- No alignment analysis started
