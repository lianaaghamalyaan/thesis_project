# Pipeline Log (Internal)

*For the thesis-friendly version, see `data_collection_log.md`.*

---

## 2026-03-21 — Initial setup

- Inspected 5 files in root folder: 1 reference CSV, 2 Apify JSONs (one duplicate), 1 Apify CSV export, 1 LinkedIn CSV
- Created project folder structure (`data/raw/`, `data/processed/`, `notebooks/`, `docs/`, etc.)
- Copied files into organized locations, duplicates → `to_review/`
- Parsed YSU batch 1 (14 pages) → 629 courses
- Identified 8 missing YSU programs + 10 non-YSU programs

## 2026-03-22 — YSU batch 2 merged

- Received 8 missing YSU pages (batch 2)
- Merged batch 1 + batch 2 → `ysu_merged.json` (22 pages)
- Re-parsed → 1,131 courses total (was 629)
- Updated `missing_programs.csv`: removed 8 resolved YSU entries, 10 remaining

## 2026-03-22 — AUA crawl assessed

- Received AUA Apify crawl (4 pages)
- Finding: overview pages only, no course tables
- Need to scrape `cse.aua.am/courses/` for actual course data
- Updated `missing_programs.csv`: AUA entries marked `crawl_status=overview_only`

## 2026-03-22 — Project cleanup

- Archived all messy Apify filenames and duplicates → `data/raw/_originals/`
- Renamed all working files to clean, consistent names
- Removed `data/to_review/` (contents moved to `_originals/`)
- Updated all notebook paths to match new file names
- Rewrote `DATA_INVENTORY.md`, `TASKS.md`
- Created `docs/data_collection_log.md` (thesis-friendly methodology reference)

## 2026-03-22 — NUACA scraped and parsed

- Received NUACA Apify crawl (5 pages, all IT/STEM programs)
- Unlike AUA, NUACA pages contain full course listings (plain text format, not markdown tables)
- Built custom parser: extracted 174 courses across 5 programs
- Saved `data/raw/university/apify/nuaca_programs_2026-03-21.json` (clean name)
- Saved `data/processed/university/nuaca_courses_parsed.csv` (174 rows)
- Updated `missing_programs.csv`: removed 5 NUACA entries, 5 remaining (4 AUA + 1 RAU)

## 2026-03-22 — AUA course catalog scraped and parsed

- Scraped `https://cse.aua.am/courses/` — single page with complete AUA course catalog
- Beautifully structured: Program, Course Code, Title, Description, Credits, Prerequisites
- Parsed 249 courses across 7 programs (4 target + 3 bonus STEM programs)
- Every course has a full English description — richest dataset of all universities
- Saved `data/raw/university/apify/aua_courses_2026-03-21.json` (clean name)
- Saved `data/processed/university/aua_courses_parsed.csv` (249 rows)
- Updated `missing_programs.csv`: 1 remaining (RAU only)

## 2026-03-22 — RAU scraped from PDF study plans

- Known URL `impht.rau.am/am/program/bachelor` was just an overview page
- Web search found official curriculum page: `rau.am/sveden/education/programs/prikladnaya-matematika-i-informatika-01.03.02.html`
- Downloaded 4 PDF study plans (Years 1–4) from that page
- Extracted text with PyPDF2, parsed course codes (Б1.О.xx, Б1.В.xx), Russian names, credits
- Initial parse: 53 rows with artifacts from PDF page breaks
- Cleaned: removed 6 duplicate/artifact entries, added English translations for all courses
- Saved `data/processed/university/rau_courses_parsed.csv` (47 rows)
- 25 mandatory + 15 elective (formative) + 7 elective (by choice) courses
- 1 course missing credits (Б1.О.09 Probability Theory and Mathematical Statistics)
- Updated `missing_programs.csv`: 0 remaining — all universities complete
