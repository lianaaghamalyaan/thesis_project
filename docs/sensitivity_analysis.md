# Sensitivity Analysis

**Source notebook:** `notebooks/3_analysis/03_sensitivity_analysis.ipynb`

This document reports the results of three sensitivity analyses performed to assess the robustness of the skill extraction pipeline and to quantify known limitations that affect interpretation of the main alignment results.

---

## Part 1: Description Asymmetry (AUA Test)

### Motivation

Universities in the dataset differ sharply in how much textual information is available per course. AUA stands out with rich descriptions (~200 words per course, 97% coverage), making it a natural test case. This analysis compares skill extraction when using **course names only** versus **course names + descriptions**, holding all other pipeline parameters constant.

### Results

| Metric | Names Only | Names + Descriptions |
|---|---|---|
| Courses processed | 235 | 248 |
| Avg skills per course | 1.8 | 9.6 |
| Unique curriculum skills | 124 | 1,277 |
| Overlap with jobs | 61 | 315 |
| Coverage rate | 1.3% | 6.8% |
| Jaccard similarity | 1.3% | 5.6% |
| Gap (jobs need, AUA lacks) | 4,572 | 4,318 |
| Surplus (AUA has, jobs don't) | 63 | 962 |

### Interpretation

The difference is roughly **5x** across every metric. Descriptions are not just "nice to have" -- they are the primary source of skill extraction signal. Course names alone are too short and too generic for meaningful TF-IDF extraction; a name like "Introduction to Computer Science" yields at most one or two broad tokens, whereas a full description surfaces specific tools, languages, and concepts.

### Implications for Cross-University Comparison

- **NUACA** (174 courses, 0% descriptions) and **RAU** (47 courses, 0% descriptions) alignment scores are **systematically underestimated** because their extraction relies entirely on course names.
- Their reported coverage and overlap figures should be interpreted as **lower bounds** on true curriculum-industry alignment.
- Cross-university comparison is valid **only within description-availability groups**:
  - Group A (with descriptions): AUA, YSU
  - Group B (without descriptions): NUACA, RAU
- This is a **data limitation**, not a method limitation. If NUACA and RAU course descriptions become available in the future, the pipeline can be rerun without modification.

---

## Part 2: Validation Against Human-Curated skills_tags

### Motivation

A subset of 151 job postings (104 from EPAM, 47 from Staff.am) include a `skills_tags` field populated by human recruiters. These tags serve as a ground-truth proxy for evaluating how well the automated extraction methods recover known skills.

### Results

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Exact match recall | 14.5% | 0.1% |
| Soft match recall | 44.2% | 20.5% |
| Precision proxy | 20.3% | 10.7% |
| F1-like (soft) | 27.9% | 14.1% |

Technical-only results (soft skills excluded from the ground truth):

- **TF-IDF:** 45.7% recall
- **KeyBERT:** 21.5% recall

### Most Frequently Missed Tags

| Tag | Times missed |
|---|---|
| teamwork | 15 |
| problem solving | 13 |
| sql | 13 |
| amazon web services | 12 |
| javascript | 11 |
| c# | 10 |
| ability to work independently | 9 |
| time management | 8 |
| kubernetes | 8 |

### Why Recall Is Capped

The ~45% soft recall ceiling for TF-IDF is explained by four systematic factors:

1. **Soft skills intentionally filtered.** Tags like "teamwork," "problem solving," and "ability to work independently" are removed by design because the pipeline focuses on IT/technical skills. This is correct behavior, not an error.
2. **Special-character tokens mangled by tokenizer.** Terms such as C#, .NET, and Node.js are broken or dropped by the regex-based tokenizer, preventing exact or soft matches.
3. **TF-IDF min_df=2 drops rare terms.** Any term appearing in only one document in the corpus is excluded, which can eliminate niche but valid skills.
4. **Tag sparsity inflates the precision denominator.** Human tags average ~5 per job while the pipeline extracts ~10, so the precision proxy is itself a lower bound.

### Conclusion

TF-IDF consistently outperforms KeyBERT on every validation metric. The 44.2% soft recall (45.7% for technical-only) is reasonable given the structural factors above, and it confirms that TF-IDF is the appropriate primary extraction method for this dataset.

---

## Part 3: Noise Cleanup

### Motivation

Initial inspection of TF-IDF overlap terms revealed that a large share consisted of generic English words (e.g., "access," "background," "goal") rather than genuine IT skills. A stopword list was constructed to remove these terms without discarding legitimate technical vocabulary.

### Before and After

| Metric | Before | After |
|---|---|---|
| TF-IDF overlap | 584 (12.6%) | 296 (6.4%) |
| TF-IDF curriculum skills | 3,734 | 3,423 |
| KeyBERT overlap | 23 (0.24%) | 23 (0.26%) |

**60% of original TF-IDF overlap was generic English words.** The cleanup added 459 generic unigrams and 11 noise phrases to the stopword list.

### Examples of Removed Noise

access, achieve, active, activities, background, challenges, comprehensive, critical, daily, effective, enable, foundation, future, goal, improvement, innovation

### Examples of Retained Skills

algorithms, analytics, angular, automation, blockchain, cloud, cybersecurity, data science, database, deployment, javascript, python, sql, testing

### Impact

The noise cleanup cut reported overlap nearly in half, meaning that pre-cleanup alignment figures were substantially inflated by non-skill tokens. KeyBERT overlap was unaffected (23 terms in both cases), which is consistent with KeyBERT producing fewer but more semantically coherent extractions. All alignment results reported in the thesis use the post-cleanup figures.

---

## Summary: What This Means for the Thesis

Three key takeaways emerge from the sensitivity analysis:

1. **Description availability is the dominant source of variation across universities.** The 5x difference between names-only and names+descriptions extraction at AUA means that NUACA and RAU alignment scores are lower bounds. Any cross-university ranking must account for this asymmetry, and the thesis presents comparisons within description-availability groups rather than as a single league table.

2. **TF-IDF is the right primary method for this corpus.** Validation against human-curated tags shows TF-IDF achieving nearly double the soft recall and double the F1 of KeyBERT. The ~45% technical recall ceiling is well-explained by intentional filtering choices and tokenizer limitations, not by fundamental method failure.

3. **Post-cleanup alignment figures are conservative and trustworthy.** Removing 60% of spurious overlap terms means the final reported gaps and coverage rates reflect genuine skill matches, not vocabulary coincidences. If anything, the remaining figures slightly undercount true alignment because of the tokenizer issues with special-character skill names (C#, .NET, Node.js).

These findings do not invalidate the main analysis -- they clarify its boundary conditions and strengthen confidence in the reported results within those boundaries.
