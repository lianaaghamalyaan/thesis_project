# ESCO Normalization Calibration Results

**Date:** 2026-03-24
**Notebook:** `notebooks/3_analysis/04_esco_calibration.ipynb`

---

## Calibration Set

- 293 phrase–ESCO pairs, stratified across 7 cosine similarity bands
- Annotated using GPT-4o-mini (temperature=0); 35-pair human spot-check at 94.3% agreement
- Match criterion: `is_match = 1` (genuine conceptual match)

## Threshold Metrics

| Threshold | Precision | Recall | F1 | Coverage |
|---|---|---|---|---|
| 0.6 | 0.468 | 0.967 | 0.631 | 0.853 |
| 0.65 | 0.541 | 0.926 | 0.683 | 0.706 |
| 0.7 | 0.616 | 0.835 | 0.709 | 0.56 |
| 0.75 | 0.711 | 0.711 | 0.711 | 0.413 **(chosen)** |
| 0.8 | 0.833 | 0.537 | 0.653 | 0.266 |
| 0.85 | 0.907 | 0.322 | 0.476 | 0.147 |

## Chosen Threshold

**0.75** — maximizes F1 score (0.711).

### Rationale

The threshold of 0.75 balances precision (avoiding false ESCO assignments) with recall (capturing all genuine matches). At this threshold, approximately 41.3% of extracted phrases are mapped to at least one ESCO concept; the remainder are retained as unmatched terms for the emerging skills category.
