# Armenian IT Curriculum — Labor Market Alignment

Master's thesis project repository.

**Research question:** How well do IT curricula from selected Armenian universities align with current Armenian IT job market demands?

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
  3_analysis/         Main analysis: IT filtering, EDA, skill extraction, sensitivity, ESCO
thesis_draft.docx     Current thesis draft export
```

---

## Pipeline Overview

```
1. Collect job postings        notebooks/1_collection_jobs/   (01–12 scraping, 13 merge)
2. Filter IT-only jobs         notebooks/3_analysis/00_filter_it_jobs.ipynb  → final_jobs_dataset_it_only.csv + audit
3. Collect curriculum data     notebooks/2_collection_university/  (01 parse, 02 translate, 03 build, 04 enrich)
4. Exploratory analysis        notebooks/3_analysis/01_eda.ipynb
5. Skill extraction            notebooks/3_analysis/02_skill_extraction.ipynb
6. Sensitivity analysis        notebooks/3_analysis/03_sensitivity_analysis.ipynb
7. ESCO calibration            notebooks/3_analysis/04_esco_calibration.ipynb  ← complete
8. ESCO annotation             notebooks/3_analysis/04b_annotate_calibration_pairs.ipynb  ← complete
9. ESCO normalization          notebooks/3_analysis/05_esco_normalization.ipynb  ← complete
10. Alignment analysis         notebooks/3_analysis/06_alignment_analysis.ipynb  ← complete
```

---

## Current State

| Stage | Status |
|---|---|
| Data collection | Complete |
| Data cleaning and structuring | Complete |
| IT-only job market filtering | Complete |
| Translation pipeline (YSU) | Complete |
| Skill extraction baseline | Complete |
| Sensitivity analysis and validation | Complete |
| ESCO normalization | Complete |
| Final alignment analysis | Complete |
| Thesis draft | In progress (Chapters 6–7 remaining) |

Current frozen analysis inputs:

- Curriculum dataset: `1,161` courses from `25` named programs across `4` universities
- Broad jobs snapshot: `1,369` postings from `14` sources
- IT-only market dataset used downstream: `753` postings from `13` sources
- ESCO-normalized alignment: TF-IDF `32.82%`, KeyBERT `28.5%`
