# Advisor Review Guide

This folder is the entry point for reviewing the project without needing to understand the full repository structure first.

## What This Project Is

A master's thesis on the alignment between IT curricula from selected Armenian universities and Armenian IT labor market demand.

The project compares:

- university curriculum text
- job posting text
- extracted skill profiles from both sides

The goal is to identify overlap, gaps, and mismatches in a structured and reproducible way.

## What Is Already Done

- Curriculum dataset: 1,161 courses, 25 programs, 4 universities
- Jobs dataset: 1,369 merged postings from 14 sources; 753 IT-only postings used in downstream analysis
- YSU Armenian content translated to English (GPT-4o-mini, validated)
- Skill extraction: TF-IDF and KeyBERT on both corpora
- Sensitivity analysis and validation against human-curated skill tags
- ESCO calibration: 293 pairs annotated, threshold 0.75 selected (F1=0.711)
- ESCO normalization: all phrases mapped to ESCO v1.2 concept identifiers
- Final alignment analysis: per-program coverage, gap/surplus breakdown, visualizations
- Emerging tech skills analysis: modern tools beyond ESCO vocabulary identified
- Skill frequency analysis: top 60 demanded skills overall + top 15 per role (9 core IT roles)
- Thesis Chapter 5 (Results): fully written with all results

## What Is Still In Progress

- Chapter 6 (Discussion) — interpretation and recommendations
- Chapter 7 (Conclusion)

## Key Results (Summary)

**Normalized curriculum–market alignment (ESCO concept level):**

| Method | Coverage |
|---|---|
| TF-IDF | 32.82% |
| KeyBERT | 28.5% |
| Analysis set | 753 IT-only job postings after filtering the 1,369-posting market snapshot |

**Per-program range:** 0.92% (NUACA GIS, Master) to 12.27% (AUA Computer and Information Science, Master).

**Most demanded skills overall** (IT-only market): Python, CI/CD, AWS, Azure, GCP, Docker, DevOps, Kubernetes, React, .NET / C#.

**Top interpretable ESCO gap skills** (demanded by market, absent from curricula): SAP R3, PHP, Java, TypeScript, SQL Server, DevOps, CSS, Android, responsive design.

**Top surplus skills** (taught but not demanded): general-education requirements (languages, humanities), advanced theory (algebra, Monte Carlo simulation, biostatistics).

## Suggested Reading Order

1. `current_status.md` — progress and results at a glance

2. `../docs/methodology_walkthrough.md` — full pipeline in plain language (with results)

3. `../docs/thesis/chapter_5_results.md` — complete results chapter

4. `../docs/skill_extraction_results.md` — pre-ESCO baseline details

5. `../docs/sensitivity_analysis.md` — robustness checks and limitations

6. `../docs/translation_decision.md` — Armenian-to-English translation rationale

7. `../docs/data_gaps_and_limitations.md` — coverage gaps and constraints

8. `feedback_questions.md` — open questions for advisor feedback

## Repository Navigation

- `../README.md` — top-level project map
- `../docs/project_overview.md` — fuller project summary
- `../docs/data_inventory.md` — file-level dataset inventory
- `../notebooks/3_analysis/` — all analysis notebooks (01–06), runnable in order

## Thesis Draft

- `../thesis_draft.docx` — current export (may lag behind the markdown chapter files)
- `../docs/thesis/` — most up-to-date chapter drafts in markdown
