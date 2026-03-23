# Project Context — Master's Thesis

## Research Question

How well do Armenian university IT/STEM curricula align with the current demands of the Armenian IT job market?

## Goal

Produce a data-driven, quantitative comparison between:
1. **University IT/STEM curricula** — what students are taught across 4 Armenian universities
2. **Armenian IT job market demands** — what employers require, from 11 job data sources

The outcome is a structured skill-gap analysis: which skills are taught but not demanded, which are demanded but not taught, and where the strongest alignment exists — broken down by university, program, and degree level.

---

## Universities in Scope

| University | Abbreviation | Programs | Courses |
|---|---|---|---|
| Yerevan State University | YSU | 13 | 691 |
| American University of Armenia | AUA | 7 | 249 |
| National University of Architecture and Construction of Armenia | NUACA | 4 | 174 |
| Russian-Armenian University | RAU | 1 | 47 |
| **Total** | | **25** | **1,161** |

**Not included (with justification):**
- NPUA (Polytech) — HTTP 403 / Cloudflare bot protection blocked all scraping attempts
- UFAR — not assessed (French-language institution, limited IT programs)
- Additional RAU programs — identified but PDF parsing out of scope

---

## Job Data Sources (after deduplication)

| Source | Type | Rows |
|---|---|---|
| LinkedIn | Aggregator | 734 |
| SoftConstruct | Company portal | 141 |
| EPAM | Company portal | 104 |
| Staff.am | Aggregator | 48 |
| job.am | Aggregator | 20 |
| Krisp | Company portal | 7 |
| DataArt | Company portal | 5 |
| ServiceTitan | Company portal | 4 |
| Synopsys | Company portal | 2 |
| Picsart | Company portal | 2 |
| DISQO | Company portal | 1 |
| **Total** | | **1,068** |

280 duplicates removed (75 within-source, 205 cross-source).

---

## Final Datasets

| Dataset | File | Rows | Status |
|---|---|---|---|
| Curriculum | `data/processed/university/final_curriculum_dataset.csv` | 1,161 | Frozen |
| Curriculum (NLP-ready) | `data/processed/university/ysu_translated.csv` | 1,161 | Frozen — includes `course_name_en` + `description_en` |
| Jobs | `data/processed/jobs/final_jobs_dataset.csv` | 1,068 | Frozen |

---

## Pipeline — Current State

```
Phase 1: Data Collection ✓ COMPLETE
  Raw scraping from 4 universities + 11 job sources

Phase 2: Data Cleaning ✓ COMPLETE
  final_curriculum_dataset.csv (1,161 rows)
  final_jobs_dataset.csv (1,068 rows, deduplicated)
  YSU course translation (Armenian → English, OpenAI gpt-4o-mini)

Phase 3: Skill Extraction ✓ COMPLETE
  TF-IDF + KeyBERT extraction from both corpora
  Noise audit: 60% of original overlap was generic English — expanded filters, re-ran
  Pre-ESCO baseline: TF-IDF 6.4%, KeyBERT 0.26%
  Validation vs skills_tags: TF-IDF 44% recall, KeyBERT 21% recall (soft match, 151 jobs)

Phase 4: ESCO Normalization ✓ COMPLETE
  293 calibration pairs annotated (GPT-4o-mini, 94.3% human agreement on 35-pair spot-check)
  Threshold: 0.75 (F1=0.711, selected by sweep across 0.60-0.85)
  All 19,998 unique phrases mapped to ESCO v1.2 concept IDs
  Normalized alignment: TF-IDF 25.2%, KeyBERT 20.3%, Union 25.7%

Phase 5: Alignment Analysis ✓ COMPLETE
  Per-program coverage: 25 programs ranked (0.6%-9.1%)
  University breakdown: AUA 5.77% > YSU 4.46% > RAU 2.28% > NUACA 1.60%
  Knowledge vs. competence split: overlap 70% knowledge / 30% competence
  Gap: 394 ESCO concepts demanded but not taught (top: Java, TypeScript, Azure, React)
  Surplus: 196 ESCO concepts taught but not demanded (state requirements + theory)
  Emerging tech analysis: 24 modern tools beyond ESCO (Azure, React, AWS, Kubernetes all gaps)
  Figures: docs/figures/per_program_coverage.png, gap_surplus_breakdown.png

Phase 6: Thesis Writing <- CURRENT STEP
  Chapter 5 (Results): complete
  Chapter 6 (Discussion): in progress
  Chapter 7 (Conclusion): not started
```

---

## Tech Stack

- **Data collection:** Python (requests, BeautifulSoup, Playwright), Apify cloud
- **Data processing:** Python (pandas, re, json, PyPDF2)
- **Translation:** OpenAI gpt-4o-mini API (691 YSU courses, Armenian → English)
- **NLP:** scikit-learn (TF-IDF), KeyBERT (all-MiniLM-L6-v2), sentence-transformers
- **Taxonomy:** ESCO v1.2 (European Skills/Competences/Occupations)
- **Visualization:** matplotlib, seaborn
- **Notebooks:** Jupyter (.ipynb) with baked outputs

---

## Key Decisions Made

- **YSU translation:** Option A chosen — translate Armenian → English using OpenAI gpt-4o-mini before extraction. Compared against Perplexity sonar-pro (OpenAI 20/20 vs Perplexity 6/20 quality scores).
- **Extraction methods:** Two unsupervised methods compared (TF-IDF + KeyBERT). Supervised approach (SkillSpan) cited as benchmark but not implemented — requires labeled training data unavailable for Armenian curriculum.
- **KeyBERT diversity:** MMR (Maximal Marginal Relevance) used instead of MaxSum — O(n·k) vs O(n²), ~6 min vs ~31 min on CPU.
- **Noise cleanup (2026-03-23):** Systematic audit of TF-IDF overlap found 60% were generic English words. Added 459 generic unigrams + 11 noise phrases to filters. Coverage dropped from inflated 12.6% to honest 6.4%.
- **Description asymmetry:** AUA sensitivity test shows 5x coverage difference (1.3% names-only vs 6.8% with descriptions). NUACA/RAU scores are lower bounds.
- **ESCO threshold:** Calibrated at 0.75 (F1=0.711). 293 pairs annotated via GPT-4o-mini, 35-pair human spot-check at 94.3% agreement. Sensitivity check confirmed threshold does not affect concept-level overlap count — bottleneck is ESCO vocabulary coverage, not threshold strictness.
- **Curriculum dataset frozen:** No new universities or courses will be added.
- **Jobs snapshot:** All data collected March 2026. No historical comparison intended.
