# Armenian IT Curriculum — Labor Market Alignment

Master's thesis project repository.

**Research question:** How well do Armenian university IT curricula align with current Armenian IT job market demands?

---

## For Advisors and Reviewers

Start here: [`for_advisor/START_HERE.md`](for_advisor/START_HERE.md)

That file explains the project, current progress, suggested reading order, and open feedback questions — without requiring any knowledge of the repository structure.

---

## Repository Structure

```
for_advisor/          Advisor entry point — start here for review
data/                 Raw and processed datasets
  raw/                Original collected data (never modified)
  processed/          Analysis-ready data
    university/       Curriculum datasets per university
    jobs/             Job posting datasets per company
    skills/           Extracted skill profiles
    esco/             ESCO normalization outputs
docs/                 Methodology, results, and project documentation
  methodology_walkthrough.md
  skill_extraction_results.md
  sensitivity_analysis.md
  translation_decision.md
  data_gaps_and_limitations.md
  project_overview.md
  data_inventory.md
  thesis/             Chapter drafts (markdown)
  process_logs/       Internal collection and pipeline logs
notebooks/            All analysis code, organized by pipeline stage
  1_collection_jobs/  Job scraping notebooks (01–13), one per source + merge
  2_collection_university/  University data collection, parsing, and building
  3_analysis/         Main analysis: EDA, skill extraction, sensitivity, ESCO
thesis_draft.docx     Current thesis draft export
```

---

## Pipeline Overview

```
1. Collect job postings        notebooks/1_collection_jobs/   (01–12 scraping, 13 merge)
2. Collect curriculum data     notebooks/2_collection_university/  (01 parse, 02 translate, 03 build, 04 enrich)
3. Exploratory analysis        notebooks/3_analysis/01_eda.ipynb
4. Skill extraction            notebooks/3_analysis/02_skill_extraction.ipynb
5. Sensitivity analysis        notebooks/3_analysis/03_sensitivity_analysis.ipynb
6. ESCO calibration            notebooks/3_analysis/04_esco_calibration.ipynb  ← complete
7. ESCO annotation             notebooks/3_analysis/04b_annotate_calibration_pairs.ipynb  ← complete
8. ESCO normalization          notebooks/3_analysis/05_esco_normalization.ipynb  ← complete
9. Alignment analysis          notebooks/3_analysis/06_alignment_analysis.ipynb  ← in progress
```

---

## Current State

| Stage | Status |
|---|---|
| Data collection | Complete |
| Data cleaning and structuring | Complete |
| Translation pipeline (YSU) | Complete |
| Skill extraction baseline | Complete |
| Sensitivity analysis and validation | Complete |
| ESCO normalization | Complete |
| Final alignment analysis | Complete |
| Thesis draft | In progress (Chapters 6–7 remaining) |
