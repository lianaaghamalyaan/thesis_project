# Current Project Status

## Short Summary

The empirical analysis is complete. All results are available. The thesis is being written up.

The current status is:

- research question defined ✓
- datasets built ✓
- preprocessing completed ✓
- IT-only market filtering completed ✓
- translation completed ✓
- baseline NLP extraction completed ✓
- validation and sensitivity analysis completed ✓
- ESCO calibration completed (293 pairs annotated, threshold 0.75, F1=0.711) ✓
- ESCO normalization completed ✓
- Final alignment analysis completed (per-program, by university, by degree, gap/surplus) ✓
- Emerging tech skills analysis completed ✓
- Skill frequency analysis completed (top 60 overall + top 15 per role, 9 core IT roles) ✓
- Chapter 5 (Results) written ✓
- Chapter 6 (Discussion) — in progress
- Chapter 7 (Conclusion) — in progress

## Core Research Flow

```text
Curriculum collection
-> curriculum cleaning and structuring
-> Armenian/Russian to English handling
-> jobs collection
-> jobs deduplication and schema merge
-> IT-only market filtering
-> skill extraction (TF-IDF, KeyBERT)
-> validation and sensitivity analysis
-> ESCO normalization [complete]
-> final alignment analysis [complete]
-> thesis write-up [in progress — Chapters 6 and 7 remaining]
```

## Datasets

### Curriculum side

- File: `data/processed/university/final_curriculum_dataset.csv`
- Rows: `1,161`
- Universities: `4`
- Named programs: `25`
- Program-degree combinations in dataset structure: `27`

Universities included:

- YSU
- AUA
- NUACA
- RAU

Known coverage limits:

- NPUA not included
- UFAR not assessed
- RAU only partially covered

### Jobs side

- File: `data/processed/jobs/final_jobs_dataset.csv`
- Rows in broad market snapshot: `1,369`
- Sources: `14`

- File: `data/processed/jobs/final_jobs_dataset_it_only.csv`
- Rows used in downstream analysis: `753`
- Sources after IT filtering: `13`

Source mix:

- aggregators: LinkedIn, Staff.am, job.am
- company portals: EPAM, SoftConstruct, Krisp, DataArt, ServiceTitan, Synopsys, Picsart, DISQO, Grid Dynamics, NVIDIA, 10Web

## What Is Methodologically Strong Already

### 1. The pipeline has clear stages

The project is not a loose notebook collection. It has a coherent analytical flow and supporting documentation.

### 2. The baseline NLP analysis is already real

This is not just a plan. Extraction has been run, outputs exist, and the comparison between methods is documented.

### 3. Validation is already included

The project does not treat raw NLP outputs as automatically valid.

Already completed:

- noise audit
- AUA description asymmetry test
- validation against human-curated `skills_tags`

### 4. Method choices are documented

Important decisions are already justified:

- translation-first approach
- OpenAI `gpt-4o-mini` over Perplexity
- TF-IDF and KeyBERT as unsupervised methods
- ESCO as the normalization target

## Best Current Results

### Pre-ESCO string-level baseline

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum unique skills | 3,442 | 4,812 |
| Job unique skills | 3,153 | 5,530 |
| Overlap | 279 | 18 |
| Coverage rate | 8.85% | 0.33% |

Validation against human-curated `skills_tags`: TF-IDF soft recall 44%, KeyBERT 21%.

### Post-ESCO normalized results (concept level)

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum ESCO concepts | 332 | 398 |
| Job market ESCO concepts | 326 | 207 |
| **Overlap** | **107** | **59** |
| **Coverage rate** | **32.82%** | **28.5%** |
| Gap (demanded, not taught) | 219 | 148 |
| Surplus (taught, not demanded) | 225 | 339 |

Coverage improved from 8.85% → 32.82% (TF-IDF) and 0.33% → 28.5% (KeyBERT) after ESCO normalization, as expected — surface-form variation collapses into shared concept IDs.

Per-program coverage ranges from 12.27% (AUA Computer and Information Science, Master) to 0.92% (NUACA GIS, Master). AUA leads consistently due to richer course descriptions and higher concept density.

## Completed Analytical Work

The full pipeline is complete. The project has:

- a valid baseline (pre-ESCO string-level overlap)
- a valid extraction comparison (TF-IDF vs KeyBERT)
- a valid validation section (sensitivity analysis, human-curated tag recall)
- a calibrated ESCO threshold (0.75, F1=0.711)
- normalized alignment results at the concept level
- per-program coverage scores for all 25 programs
- skill frequency ranking (top 60 overall, top 15 per role across 9 core IT roles)
- all outputs saved to `data/processed/esco/` and `data/processed/skills/`

## Main Open Step

Thesis write-up — Chapters 6 (Discussion) and 7 (Conclusion) are in progress.

## Main Current Limitations

### Description asymmetry

AUA has rich descriptions, while NUACA and RAU rely mostly on course names.

This creates a structural measurement bias.

### Translation dependence

YSU relies on machine translation before extraction.

### Dataset coverage

The Armenian higher education side is not complete.

### Unsupervised extraction ceiling

The project uses unsupervised methods, so recall is meaningful but not perfect.

## Why This Is a Good Time for Feedback

This is a strong stage for expert feedback because:

- the project is concrete enough to review seriously
- the main methodological tradeoffs are now visible
- there is still enough time to improve the design if needed

In other words, the project is mature enough for expert review, but not so late that feedback would be hard to apply.
