# Feedback Questions for Advisor Review

The empirical analysis is complete. The questions below are the main areas where advisor input would be most valuable before finalizing the thesis.

---

## 1. Interpretation of the 25% Coverage Finding

The ESCO-normalized analysis shows ~25% of job-market skill concepts are covered by Armenian IT curricula. Is this framing appropriate:

- Presented as a lower bound (ESCO v1.2 vocabulary gap, description asymmetry at NUACA/RAU)
- The "true" alignment is likely higher but not measurable with this approach
- Is 25% a finding worth reporting as a headline number, or should the emphasis shift to the gap/surplus breakdown instead?

## 2. Knowledge vs. Competence Split

The overlap is 70% *knowledge* concepts and 30% *skill/competence* concepts. The gap is 51% applied competences. This suggests curricula share the right knowledge domains with employers but fall short on applied practice.

- Is this distinction (ESCO's knowledge/skill-competence taxonomy) well-known enough to use without extensive justification?
- Does this finding support a strong recommendation about curriculum reform (add practical labs, industry projects) or is it too indirect?

## 3. SoftConstruct Effect in the Gap

SoftConstruct (gambling/gaming company, 141 postings = 13% of the dataset) inflates the gap with domain-specific concepts (betting, gambling games, manage casino). These appear in the gap alongside genuine IT skills.

- Should these be filtered out of the gap analysis entirely?
- Or reported separately as "domain-specific employer demand" to distinguish from general IT skill gaps?

## 4. ESCO Vocabulary Gap

Docker, React, Azure, Kubernetes, Node.js are not in ESCO v1.2. The emerging tech analysis identifies these via a curated lexicon, but they cannot contribute to the main ESCO-normalized metric.

- Is it methodologically clean to report two parallel analyses (ESCO + tech lexicon supplement)?
- Or should this be framed purely as a limitation?

## 5. Cross-University Comparability

AUA results are most reliable (full English descriptions). NUACA and RAU are lower bounds due to name-only course data. 48% of NUACA courses and 56% of RAU courses contribute zero ESCO concepts.

- How strongly should cross-university comparisons be qualified?
- Is the AUA vs. YSU comparison valid given they both have full descriptions (though YSU's are machine-translated)?

## 6. Discussion Chapter — Recommendations

The Discussion chapter will include curriculum reform recommendations. Which framing is more appropriate for an Armenian higher-education context:

- **Program-level:** specific programs should add specific skills
- **University-level:** institutional policies (e.g. more industry partnerships, capstone projects)
- **System-level:** accreditation standards should require regular labor market alignment checks

## 7. Overall Scope and Claims

Given the dataset covers ~50% of Armenian IT higher education (NPUA and UFAR excluded), how cautious should the generalization claims be?

---

## Optional Review Files

| File | What it contains |
|---|---|
| `current_status.md` | Progress and key numbers at a glance |
| `../docs/methodology_walkthrough.md` | Full pipeline in plain language |
| `../docs/thesis/chapter_5_results.md` | Complete results chapter |
| `../docs/skill_extraction_results.md` | Pre-ESCO extraction details |
| `../docs/sensitivity_analysis.md` | Robustness checks |
| `../docs/esco_calibration_results.md` | Threshold calibration detail |
| `../docs/data_gaps_and_limitations.md` | University coverage constraints |
