# Skill Extraction Results — Phase 3 (Cleaned)

**Date:** 2026-03-25 (updated after noise cleanup and IT-only market filtering)
**Notebook:** `notebooks/3_analysis/02_skill_extraction.ipynb`
**Outputs:** `data/processed/skills/`

---

## What Was Done

Ran the complete skill extraction pipeline on both corpora. After the initial run, performed a systematic noise audit that identified 60% of TF-IDF overlap terms as generic English words (not skills). Expanded the stopword/filter lists and re-ran.

### Preprocessing pipeline:
1. **Boilerplate removal** — 140 paragraphs appearing in 4+ jobs stripped
2. **Custom stopwords** — 295 terms: academic filler, job posting noise, geography
3. **Company name token filter** — tokens from 434 company names blocked
4. **Generic unigram filter** — 459 terms: common English words that are not skills (`access`, `achieve`, `activities`, `background`, `challenges`, etc.)
5. **Multi-word noise phrases** — 11 specific bigrams blocked (`cutting edge`, `wide range`, `data data`, etc.)
6. **`is_skill_like()` post-filter** — rejects pure numbers, all-stopword n-grams (threshold: >60% stop ratio)
7. **KeyBERT MMR diversity** — `use_mmr=True`, `diversity=0.5`

---

## Results (after noise cleanup)

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Curriculum unique skills | 3,442 | 4,812 |
| Job unique skills | 3,153 | 5,530 |
| Overlap | 279 | 18 |
| Coverage rate | **8.85%** | 0.33% |
| Jaccard similarity | 4.42% | 0.17% |
| Gap (jobs only) | 2,874 | 5,512 |
| Surplus (curriculum only) | 3,163 | 4,794 |

### Comparison with pre-cleanup run:

| Metric | Before (noisy) | After (cleaned) | Change |
|---|---|---|---|
| TF-IDF overlap | 584 (12.6%) | 279 (8.85%) | -305 noisy terms removed |
| TF-IDF curriculum skills | 3,734 | 3,442 | -292 |
| KeyBERT overlap | 23 (0.24%) | 18 (0.33%) | Cleaner but still sparse |

The inflated 12.6% was caused by generic English words (`access`, `achieve`, `activities`, `challenges`, etc.) appearing in both corpora. The cleaned 8.85% reflects the stronger but more realistic overlap after both noise filtering and IT-only job-market scoping.

### Why TF-IDF >> KeyBERT at raw level:
TF-IDF extracts corpus vocabulary — same word forms appear in both corpora ("data", "algorithms", "programming"). KeyBERT extracts semantically representative keyphrases per document, which are idiomatic and rarely match verbatim across corpora ("object oriented programming" vs "backend development"). After ESCO normalization maps both to shared concept IDs, KeyBERT coverage is expected to rise significantly.

### Top overlapping skills (TF-IDF, cleaned):
agile, algorithms, analysis, analytics, angular, applications, architecture, automation, big data, blockchain, cloud, code, coding, computer vision, computing, cryptography, cybersecurity, data, data analysis, data engineering, data science, data structures, database, databases, debugging, deployment, design, digital, distributed computing, encryption, etl, excel, forecasting, framework, generative ai, graphics, javascript, kotlin, machine, mining, mobile, modeling, monitoring, network, nosql, optimization, programming, python, regression, security, software, software engineering, sql, statistics, testing, visualization, vlsi, web

---

## Sensitivity Analysis: Description Asymmetry

AUA sensitivity test (names-only vs names+descriptions):

| Metric | Names Only | Names+Descriptions |
|---|---|---|
| Avg skills/course | 1.8 | 9.6 |
| Coverage rate | 1.3% | 6.8% |

**Conclusion:** Descriptions provide a 5x multiplier on coverage. NUACA and RAU (which lack descriptions) are systematically underestimated. Their alignment scores should be interpreted as lower bounds.

---

## Known Remaining Issues (pre-ESCO)

1. Some borderline terms remain (`mindset`, `drug`, `cells`) — ESCO normalization removes some of this noise, but broader concept filtering is still needed in the final analysis layer
2. Russian-language phrases in KeyBERT job output — ESCO will not match these
3. Description asymmetry means NUACA/RAU results are lower bounds

These are acceptable for a pre-normalization baseline.

---

## ESCO Normalization Results (Phase 4 — Complete)

ESCO normalization has been completed. See `docs/methodology_walkthrough.md` and `docs/thesis/chapter_5_results.md` for full results.

**Summary:**

| Method | Pre-ESCO | Post-ESCO | Improvement |
|---|---|---|---|
| TF-IDF | 8.85% | 32.82% | +23.97pp |
| KeyBERT | 0.33% | 28.5% | +28.17pp |

The improvement confirms that ESCO normalization collapses surface-form variation (e.g. "object oriented programming" and "OOP principles") into shared concept IDs. It substantially reduces terminology mismatch, although some broad ESCO concepts still require filtering and interpretation in the final analysis layer.

**Key files produced:**
- `data/processed/esco/phrase_to_esco.csv` — all phrase → ESCO concept mappings
- `data/processed/esco/alignment_normalized.json` — overlap/gap/surplus at concept level
- `data/processed/esco/alignment_per_program.csv` — per-program coverage (25 programs)
- `data/processed/esco/gap_analysis.csv` — top gap skills ranked by job market frequency
- `data/processed/esco/emerging_tech_skills.csv` — modern tools beyond ESCO vocabulary
- `docs/figures/per_program_coverage.png` — bar chart of all 25 programs
- `docs/figures/gap_surplus_breakdown.png` — top gap and surplus skills
