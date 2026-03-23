# Data Processing Pipeline

*Dataset: `data/processed/university/final_curriculum_dataset.csv`*
*Built by: `scripts/build_final_curriculum.py`*
*Date: 2026-03-22*
*Purpose: Final thesis analysis dataset — curriculum side of the curriculum–job-market alignment study.*

---

## 1. Overview

This document describes how the four parsed university curriculum datasets were merged into a single unified analysis file. It covers source files, schema decisions, format harmonisation, cleaning steps, and intentional non-cleaning decisions.

**Final output:** 1,161 course rows across 4 universities, 26 programs, 2 degree levels (Bachelor/Master) + 1 general-education category.

| University | Input rows | Rows removed | Final rows | Reason for removal |
|---|---|---|---|---|
| YSU | 820 | 129 | 691 | Exact within-program duplicates |
| AUA | 249 | 0 | 249 | None |
| NUACA | 174 | 0 | 174 | None |
| RAU | 47 | 0 | 47 | None |
| **Total** | **1,290** | **129** | **1,161** | |

---

## 2. Source Files

| File | Rows | Format | Language | Original source |
|---|---|---|---|---|
| `data/processed/university/ysu_courses_parsed.csv` | 820 | CSV, UTF-8 | Armenian | Web scrape (Apify → markdown → regex parser) |
| `data/processed/university/aua_courses_parsed.csv` | 249 | CSV, UTF-8 | English | Web scrape (Apify, structured catalog) |
| `data/processed/university/nuaca_courses_parsed.csv` | 174 | CSV, UTF-8 with BOM | English | Web scrape (Apify, plain-text course listings) |
| `data/processed/university/rau_courses_parsed.csv` | 47 | CSV, UTF-8 | Russian + English | PDF study plan (PyPDF2 + regex) |

These files were produced during Phase 1 (Data Collection). They are not modified by this pipeline — this script reads them as immutable inputs and writes a new output file.

---

## 3. Schema Design

### 3.1 Column list

| Column | Type | Source(s) | Notes |
|---|---|---|---|
| `course_id` | int | Generated | Sequential 1-based integer. Stable within this dataset version. Not a database key — for row reference only. |
| `university` | string | All | Full official English name. |
| `program_name` | string | All | English program name. YSU names corrected via URL-based mapping (see `data_collection_log.md`). |
| `program_code` | string | YSU, AUA | YSU speciality code (e.g. `061101.02.6`); AUA program abbreviation (e.g. `BSCS`). Blank for NUACA, RAU. |
| `degree_level` | string | All | `Bachelor`, `Master`, or `General`. |
| `course_code` | string | AUA, NUACA, RAU | AUA: `CS100`-style code. NUACA: `6.22ICS001`-style module code. RAU: Russian federal code (`Б1.О.01`). YSU uses only a chair/department code (stored here). Blank where unavailable. |
| `course_name` | string | All | Best available English name. For YSU: Armenian name is used directly (no English translation in source). For RAU: English translation from the PDF. |
| `course_name_original` | string | RAU only | Original-language name when different from `course_name`. RAU: Russian name. Blank for YSU (Armenian IS the original), AUA, NUACA (English originals). |
| `credits` | float | All | Credit hours. Blank where unavailable. Credit systems differ across universities — see Section 5.2. |
| `component` | string | YSU, RAU, (NUACA via assessment) | Normalized curriculum component: `General`, `Professional`, `Mandatory`, `Elective`, `Other`. Blank for AUA (component not recorded in source). |
| `semester` | int | NUACA only | Semester number (1–8). Blank for YSU, AUA, RAU. |
| `description` | string | AUA only | Full course description text. Blank for all other universities. |
| `prerequisites` | string | AUA only | Prerequisite course codes or level requirements. Blank for all other universities. |
| `assessment` | string | NUACA only | Assessment type: `Exam` or `Test`. Blank for all other universities. |
| `academic_year` | string | YSU only | Academic year string (e.g. `2025/2026`). Blank for all other universities. |
| `source_url` | string | All | URL of source page or file reference for provenance. |
| `source_language` | string | All | Language of original source data: `Armenian`, `English`, or `Russian`. Indicates what language `course_name` is in for YSU and RAU. |
| `notes` | string | Generated | Data quality flags. Blank when no issues. See Section 4.3. |

### 3.2 Schema rationale

The schema is designed as a wide, flat table optimised for NLP-phase processing rather than normalised relational storage. Key decisions:

- **`course_name` carries the Armenian/Russian name for YSU/RAU** rather than leaving it blank until translation. Translation is an NLP step, not a data collection step. Having the original name in `course_name` means NLP tools can immediately operate on it without additional join logic.

- **Columns not present in all sources are kept with blanks** (e.g. `description`, `prerequisites`, `semester`). This is preferable to dropping them — future analysis can exploit AUA descriptions for rich skill extraction while ignoring the blank fields from other universities.

- **`source_language` is explicit** so that downstream NLP code can branch logic by language without inspecting course names or university names.

- **`program_code` preserves YSU speciality codes** even though `program_name` provides the English name. The code links back to the official Armenian accreditation system and is useful for cross-referencing with ANQA documentation.

- **`course_id` is sequential and not a semantic key.** It is purely for stable row reference in notebooks. Proper joins should use `(university, program_name, course_code, course_name)`.

---

## 4. Harmonisation Decisions

### 4.1 University formats

Each university had a different source format requiring different parsing strategies:

**YSU (Armenian):** Source is markdown text converted from HTML course-plan pages. Courses appear in tables with columns: chair code, Armenian course name, credits. Curriculum component is inferred from `###` section headers. No English course names available in the scraped data. The `program_name` field required URL-based correction: official Armenian speciality codes (e.g. "056201 Statistics") did not reflect actual program names (e.g. "Applied Statistics and Data Science"). See `data_collection_log.md` for the full mapping.

**AUA (English):** Source is a single structured HTML page (`cse.aua.am/courses/`) listing all programs in a consistent format. Provides the richest metadata: full English descriptions, course codes, prerequisites, and credit values. No harmonisation issues — directly mapped to schema fields.

**NUACA (English):** Source is plain-text course listings organised by semester. Clean English names, module codes, semester numbers. One formatting inconsistency corrected (see Section 4.2). Four Physical Training entries have no module code or credits — legitimate non-credit PE requirements, kept and flagged.

**RAU (Russian/English):** Source is a PDF study plan for Russian federal program 01.03.02. Parsed with PyPDF2. Already provides both Russian and English names — Russian name preserved in `course_name_original`. Component nomenclature translated from Russian federal system (`Б1.О` → Mandatory, `Б1.В` elective tracks → Elective).

### 4.2 Normalisations applied

| Issue | Affected rows | Action | Rationale |
|---|---|---|---|
| YSU exact within-program duplicates | 129 rows | Removed | All 129 duplicates were confirmed to be within the same program and source URL — scraping artefacts from courses appearing twice in a page's markdown. No cross-program course sharing was found. |
| NUACA assessment `"Exam."` vs `"Exam"` | 63 rows | Normalised `"Exam."` → `"Exam"` | Trailing period is a data entry inconsistency in the source page; both tokens represent the same assessment type. |
| NUACA BOM (byte-order mark) | File header | Handled via `utf-8-sig` encoding | BOM present in source file; stripped automatically on read, does not affect data. |
| RAU component labels | 47 rows | Mapped to English: `Mandatory`, `Elective` | Source used Russian federal labels (`Б1.О`, `Б1.В`). Mapped to English equivalents. The distinction between "elective formative" and "elective by choice" was collapsed to `Elective` — the sub-distinction is available in the source file if needed. |

### 4.3 Flags added (notes column)

8 rows were flagged rather than modified:

| Flag | Count | Rows | Meaning |
|---|---|---|---|
| `placeholder_name` | 2 | YSU Blockchain and Digital Currencies | Source lists elective slots without course titles (`---`). These are real curriculum slots — the university has not published the elective name for the current academic year. Kept because the slot itself carries information (elective credits = curriculum flexibility). |
| `zero_credits` | 1 | YSU Radiophysics | "Մշակութաբանության հիմունքներ" (Foundations of Cultural Studies) recorded as 0 credits in the source. Kept because removal would be a silent data change. May be a non-graded activity or a data entry error in the source. |
| `non_credit_activity` | 4 | NUACA Physical Training | Physical Training entries have no module code and no credit value. This is a legitimate structural feature of the NUACA curriculum, not a parsing error. |
| `missing_credits` | 1 | RAU Probability Theory and Mathematical Statistics | Credit value absent in the PDF source page. Not a parsing failure — the table cell is empty in the original. |

---

## 5. Intentional Non-Cleaning Decisions

### 5.1 Armenian course names not translated

YSU course names are in Armenian only. They have not been translated to English in this pipeline. Reasons:
- Automated translation (Google Translate, DeepL) introduces errors for technical course titles
- The reference dataset (`data/raw/university/reference_curriculum.csv`) contains manually translated English equivalents for some YSU courses but not all, and the mapping is not complete
- Translation is a distinct NLP/preprocessing step that should be documented separately in the skill-extraction pipeline
- Keeping Armenian names preserves the original signal; NLP models that support multilingual input (e.g. `paraphrase-multilingual-mpnet-base-v2`) can operate directly on Armenian text

### 5.2 Credit systems not normalised across universities

Credit values are kept as-is from each source. The four universities use different credit systems:
- **YSU:** Armenian ECTS-compatible credits (typical range 2–9 per semester course)
- **AUA:** American credit-hour system (3 credits = one semester course)
- **NUACA:** Similar to ECTS (range 1–20, with outlier)
- **RAU:** Russian Zacunit/hour system (range 1–17; typically higher numbers than ECTS)

Normalising credits would require a conversion factor that is not standardised between systems. Credit values in this dataset should not be compared directly across universities. For alignment analysis, credit presence/absence matters more than exact values.

### 5.3 Same course name across universities is not deduplicated

"Object-Oriented Programming" appears in both NUACA and other programs. These are not deduplicated — each occurrence represents a distinct institutional offering. Cross-university deduplication would incorrectly erase information about which institutions teach the same subject.

### 5.4 Prerequisites not parsed into a graph structure

AUA prerequisites are kept as raw text strings (e.g. `"CS108, CS121 or equivalent"`). Parsing these into a structured prerequisite graph is a separate task not required for the alignment analysis in this thesis.

### 5.5 Component categories not fully harmonised across universities

Each university labels curriculum components differently:
- YSU: General / Professional / Other
- RAU: Mandatory / Elective
- NUACA: (no component field — semester structure used instead)
- AUA: (no component field — courses are part of a program with fixed/elective roles)

A unified component taxonomy would require knowledge of each university's internal degree-plan structure. Partial mapping has been applied where safe (see Section 4.2). Full harmonisation is out of scope for the data collection phase and would introduce interpretation errors.

### 5.6 AUA corequisites not included

6 AUA courses (all in Engineering Sciences) have corequisite fields. This column was not included in the final schema because:
- Only 6/249 AUA courses have values (97.6% empty)
- The information is recoverable from `aua_courses_parsed.csv` if needed
- Engineering Sciences courses are borderline for the IT alignment focus of this thesis

---

## 6. Output File

**File:** `data/processed/university/final_curriculum_dataset.csv`
**Encoding:** UTF-8 (no BOM)
**Rows:** 1,161
**Columns:** 18

| University | Rows | Programs | Bachelor | Master | General |
|---|---|---|---|---|---|
| Yerevan State University | 691 | 13 | 436 | 255 | 0 |
| American University of Armenia | 249 | 7 | 136 | 86 | 27 |
| National University of Architecture and Construction | 174 | 4 | 118 | 56 | 0 |
| Russian-Armenian University | 47 | 1 | 47 | 0 | 0 |
| **Total** | **1,161** | **25** | **737** | **397** | **27** |

> Note: `program_name` × `university` gives 25 unique combinations. NUACA has two programs sharing the name "Informatics (Computer Science)" at different degree levels — they are distinguished by `degree_level`.

---

## 7. What This Dataset Does Not Contain

- **Job market data** — handled separately in `data/raw/jobs/` and processed in Phase 2 (jobs pipeline)
- **Skill labels** — extracted in Phase 3 (NLP pipeline)
- **English translations of Armenian course names** — available from `reference_curriculum.csv` for some courses
- **Full YSU course descriptions** — not available in the scraped data; YSU pages embed descriptions within table cells but extraction was not attempted for this phase
- **NPUA data** — inaccessible (HTTP 403); documented in `docs/data_gaps_and_limitations.md`
- **UFAR data** — not assessed; documented in `docs/data_gaps_and_limitations.md`
- **Additional RAU programs** — identified but not parsed; documented in `docs/data_gaps_and_limitations.md` and `missing_programs.csv`

---

*For data collection methods and scraping technical details, see `docs/data_collection_log.md`.*
*For coverage gaps and limitations, see `docs/data_gaps_and_limitations.md`.*
