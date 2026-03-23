# Thesis Structure and Status

**Title:** Measuring the Alignment Between Armenian IT University Curricula and Labor Market Skill Demands: A Computational NLP Analysis

**Program:** [program name]
**Institution:** [institution]
**Year:** 2026

---

## File Map

| File | Status | Notes |
|---|---|---|
| `abstract.md` | ✓ Draft complete | ~350 words; fill in supervisor/program fields |
| `chapter_1_introduction.md` | ✓ Complete | 7 sections; all citations verified |
| `chapter_2_literature_review.md` | ✓ Complete | 7 sections; all citations verified |
| `chapter_3_theoretical_framework.md` | ✓ Complete | 6 sections; all citations verified |
| `chapter_4_methodology.md` | ✓ Complete | Full detail; accurate numbers after noise cleanup |
| `chapter_5_results.md` | ⚠️ Partial | Pre-ESCO sections done; Sections 5.4–5.5 await ESCO results |
| `chapter_6_discussion.md` | ⚠️ Partial | Skeleton complete; Sections 6.3 (RQ3/RQ4) await ESCO results |
| `chapter_7_conclusion.md` | ✓ Complete | Finalize numbers after ESCO results; structure is final |
| `references.md` | ⚠️ Draft | All verified citations included; 3 URLs missing (⚠️ in file) |

---

## Thesis Structure (Table of Contents)

```
ABSTRACT

TABLE OF CONTENTS

CHAPTER 1: INTRODUCTION
  1.1  Background and Motivation
  1.2  Problem Statement
  1.3  Research Objectives
  1.4  Research Questions
  1.5  Contribution of the Thesis
  1.6  Scope and Limitations
  1.7  Structure of the Thesis

CHAPTER 2: LITERATURE REVIEW
  2.1  The Curriculum–Labor Market Gap: An Established Problem
  2.2  Computational Approaches to Curriculum Alignment
  2.3  NLP Methods for Skill Extraction
  2.4  Skill Taxonomies as Measurement Frameworks
  2.5  The Armenian and Post-Soviet Educational Context
  2.6  Constructive Alignment and the Theoretical Case for Measurement
  2.7  Summary and Research Gap

CHAPTER 3: THEORETICAL FRAMEWORK
  3.1  Overview
  3.2  Constructive Alignment (Biggs & Tang, 2011)
  3.3  Task-Based View of Skill Demand (Autor, Levy & Murnane, 2003)
  3.4  ESCO as the Operational Bridge
  3.5  Integration of the Three Frameworks
  3.6  Summary

CHAPTER 4: DATA AND METHODOLOGY
  4.1  Research Design
  4.2  Curriculum Dataset
    4.2.1  Sources and Collection Strategy
    4.2.2  Data Processing and Schema
    [continues...]
  4.3  Job Market Dataset
  4.4  Translation Pipeline
  4.5  Skill Extraction Pipeline
    4.5.1  Preprocessing
    4.5.2  TF-IDF Extraction
    4.5.3  KeyBERT Extraction
    4.5.4  Post-Extraction Filtering
    4.5.5  Alignment Metrics
    4.5.6  Noise Audit and Filter Expansion
    4.5.7  Sensitivity Analyses
      4.5.7.1  Description Asymmetry
      4.5.7.2  Validation Against Human-Curated Skill Tags
      4.5.7.3  Noise Audit Summary
  4.6  ESCO Normalization
  4.7  Ethical and Methodological Considerations

CHAPTER 5: RESULTS
  5.1  Overview
  5.2  Dataset Characteristics
    5.2.1  Curriculum Dataset
    5.2.2  Job Market Dataset
  5.3  Skill Extraction Results (Pre-ESCO Baseline)
    5.3.1  Extraction Configuration
    5.3.2  Unique Skills Extracted
    5.3.3  Pre-ESCO Alignment Metrics
    5.3.4  Divergence Between TF-IDF and KeyBERT
    5.3.5  Skills in the Overlap, Gap, and Surplus
  5.4  ESCO-Normalized Alignment Results  ⏳
    5.4.1  ESCO Threshold Calibration
    5.4.2  Coverage After Normalization
    5.4.3  Top Demanded ESCO Skills Not in Curricula
    5.4.4  Top Taught ESCO Skills Not in Job Market
  5.5  Per-University and Per-Program Results  ⏳
    5.5.1  University-Level Alignment Scores
    5.5.2  Program-Level Alignment Scores
    5.5.3  Bachelor vs. Master Degree Comparison
  5.6  Sensitivity Analyses
    5.6.1  Description Asymmetry (AUA Test)
    5.6.2  Validation Against Human-Curated Tags
    5.6.3  Noise Audit
  5.7  Summary of Results

CHAPTER 6: DISCUSSION
  6.1  Overview
  6.2  Interpreting the Findings Through the Theoretical Frameworks
    6.2.1  Constructive Alignment Lens
    6.2.2  Task-Based Lens
    6.2.3  ESCO Lens  ⏳
  6.3  Addressing the Research Questions
    RQ1: Most frequently demanded skills
    RQ2: Most prevalent curriculum competences
    RQ3: Overall alignment magnitude  ⏳
    RQ4: Per-program alignment ranking  ⏳
  6.4  Comparison with Prior Studies
  6.5  Limitations
    6.5.1  Data Coverage Limitations
    6.5.2  Description Asymmetry
    6.5.3  Translation Quality
    6.5.4  Unsupervised Extraction Ceiling
    6.5.5  ESCO Coverage Lag
  6.6  Implications for Policy and Practice

CHAPTER 7: CONCLUSION
  7.1  Summary of the Study
  7.2  Contributions
  7.3  Recommendations
  7.4  Future Research
  7.5  Closing Remarks

REFERENCES
```

---

## What Remains (Blocking on ESCO)

| Task | Blocker | Output needed |
|---|---|---|
| Run `notebooks/04_esco_calibration.ipynb` cells 1–11 | — (ready to run) | `calibration_pairs.csv` |
| Manually annotate ~200 calibration pairs | Requires human judgment | `calibration_pairs.csv` with `is_match` column filled |
| Re-run cells 13–15 to choose threshold | Needs annotation above | Optimal similarity threshold |
| Run `notebooks/05_esco_normalization.ipynb` | Needs threshold above | ESCO-mapped skill sets |
| Populate Sections 5.4, 5.5 of Chapter 5 | Needs normalization above | Per-program alignment scores |
| Populate Sections 6.2.3, 6.3 RQ3/RQ4 | Needs Ch.5 above | Discussion of ESCO results |

---

## Estimated Page Budget

*(Approximate, assuming standard 12pt, 1.5 spacing)*

| Chapter | Current lines | Est. pages |
|---|---|---|
| Abstract | 1 page | 1 |
| Ch. 1 Introduction | ~65 lines | 4–5 |
| Ch. 2 Literature Review | ~110 lines | 8–10 |
| Ch. 3 Theoretical Framework | ~93 lines | 6–8 |
| Ch. 4 Methodology | ~430 lines | 20–25 |
| Ch. 5 Results | ~250 lines draft | 15–20 (with ESCO tables) |
| Ch. 6 Discussion | ~200 lines draft | 12–15 |
| Ch. 7 Conclusion | ~130 lines | 6–8 |
| References | ~40 refs | 3–4 |
| **Total** | | **~75–95 pages** |

This is within the typical range for a data-intensive master's thesis (60–100 pages).
