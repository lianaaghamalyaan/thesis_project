# Notebooks

All analysis code, organized by pipeline stage. Run them in the order below.

---

## Stage 1 — Job Data Collection (`1_collection_jobs/`)

One notebook per job source. Already collected — only re-run to refresh the dataset.

| Notebook | Source |
|---|---|
| `01_linkedin_jobs_pipeline.ipynb` | LinkedIn Armenia |
| `02_staffam_scraping.ipynb` | Staff.am |
| `03_jobam_scraping.ipynb` | Job.am |
| `04_picsart_scraping.ipynb` | Picsart |
| `05_krisp_scraping.ipynb` | Krisp |
| `06_servicetitan_scraping.ipynb` | ServiceTitan |
| `07_epam_scraping.ipynb` | EPAM |
| `08_softconstruct_scraping.ipynb` | SoftConstruct |
| `09_disqo_scraping.ipynb` | DISQO |
| `10_synopsys_scraping.ipynb` | Synopsys |
| `11_dataart_scraping.ipynb` | DataArt |
| `12_jobs_deduplication.ipynb` | Deduplicate all sources |
| `13_merge_all_sources.ipynb` | Merge into `final_jobs_dataset.csv` |

---

## Stage 2 — University Data Collection (`2_collection_university/`)

| Notebook | Purpose |
|---|---|
| `01_university_pipeline.ipynb` | Parse scraped university course data (YSU, AUA, NUACA, RAU) |
| `02_ysu_translation.ipynb` | Translate YSU Armenian/Russian course names to English |
| `03_build_curriculum.ipynb` | Merge all universities into `final_curriculum_dataset.csv` |
| `04_enrich_ysu_courses.ipynb` | Enrich YSU rows with semester, description, assessment (live HTTP) |

---

## Stage 3 — Analysis (`3_analysis/`)

Run in order after stages 1–2 are complete.

| Notebook | Purpose |
|---|---|
| `01_eda.ipynb` | Exploratory data analysis of curriculum and jobs datasets |
| `02_skill_extraction.ipynb` | TF-IDF and KeyBERT skill extraction + alignment baseline |
| `03_sensitivity_analysis.ipynb` | Robustness checks, noise audit, validation against `skills_tags` |
| `04_esco_calibration.ipynb` | ESCO embedding-based normalization and threshold calibration |
| `04b_annotate_calibration_pairs.ipynb` | GPT-4o-mini annotation of calibration pairs + 35-pair manual validation |
| `05_esco_normalization.ipynb` | Map all phrases to ESCO concepts; compute normalized alignment metrics |
| `06_alignment_analysis.ipynb` | Final results: per-program coverage, gap/surplus breakdowns, charts |

---

## Notes

- All notebooks resolve paths relative to the project root — open Jupyter from `thesis_data/`.
- Outputs are written to `data/processed/` — already frozen, do not re-run collection stages unless refreshing data.
- Stage 3 notebooks (`3_analysis/`) are the main analytical output of the thesis.
