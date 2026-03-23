# Current Project Status

## Short Summary

The empirical analysis is complete. All results are available. The thesis is being written up.

The current status is:

- research question defined ✓
- datasets built ✓
- preprocessing completed ✓
- translation completed ✓
- baseline NLP extraction completed ✓
- validation and sensitivity analysis completed ✓
- ESCO calibration completed (293 pairs annotated, threshold 0.75, F1=0.711) ✓
- ESCO normalization completed ✓
- Final alignment analysis completed (per-program, by university, by degree, gap/surplus) ✓
- Emerging tech skills analysis completed ✓
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
- Rows after deduplication: `1,068`
- Sources: `11`

Source mix:

- aggregators: LinkedIn, Staff.am, job.am
- company portals: EPAM, SoftConstruct, Krisp, DataArt, ServiceTitan, Synopsys, Picsart, DISQO

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
| Curriculum unique skills | 3,423 | 4,801 |
| Job unique skills | 4,625 | 8,695 |
| Overlap | 296 | 23 |
| Coverage rate | 6.4% | 0.26% |

Validation against human-curated `skills_tags`: TF-IDF soft recall 44%, KeyBERT 21%.

### Post-ESCO normalized results (concept level)

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum ESCO concepts | 329 | 397 |
| Job market ESCO concepts | 527 | 380 |
| **Overlap** | **133** | **77** |
| **Coverage rate** | **25.2%** | **20.3%** |
| Gap (demanded, not taught) | 394 | 303 |
| Surplus (taught, not demanded) | 196 | 320 |

Coverage improved from 6.4% → 25.2% (TF-IDF) and 0.26% → 20.3% (KeyBERT) after ESCO normalization, as expected — surface-form variation collapses into shared concept IDs.

Per-program coverage ranges from 9.1% (AUA Computer and Information Science, Master) to 0.6% (NUACA GIS, Master). AUA leads consistently due to richer course descriptions.

## Main Open Step

The ESCO-normalized alignment metrics are now produced. The remaining work is the final analysis notebook (`06_alignment_analysis.ipynb`) which will add visualizations, per-category breakdowns, and the interpretation layer for thesis Chapter 5.

The project currently has:

- a valid baseline
- a valid extraction comparison
- a valid validation section
- a calibrated ESCO threshold (0.75, F1=0.711)
- normalized alignment results at the concept level
- per-program coverage scores for all 25 programs

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
