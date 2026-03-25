# Chapter 5: Results

---

## 5.1 Overview

This chapter reports the empirical findings of the study in six parts. Section 5.2 describes the characteristics of the two datasets. Section 5.3 presents the pre-ESCO baseline alignment results from TF-IDF and KeyBERT extraction. Section 5.4 presents the ESCO-normalized alignment results, including calibration, coverage, knowledge/competence breakdown, emerging tech skills, and gap/surplus analysis. Section 5.5 presents per-university and per-program breakdowns. Section 5.6 reports the sensitivity analyses validating the robustness of the extraction. Section 5.7 summarizes the key findings.

---

## 5.2 Dataset Characteristics

### 5.2.1 Curriculum Dataset

The final curriculum dataset contains 1,161 courses across 25 programs from four universities.

**Table 5.1 — Curriculum dataset summary**

| University | Programs | Courses | Avg. credits | Description available |
|---|---|---|---|---|
| YSU | 13 | 691 | 4.8 | Full text (translated from Armenian) |
| AUA | 7 | 249 | 3.0 | Full text (English original) |
| NUACA | 4 | 174 | — | Course name only |
| RAU | 1 | 47 | — | Course name only (translated from Russian) |
| **Total** | **25** | **1,161** | — | |

Of the 1,161 courses, 28 were too short (fewer than 3 meaningful tokens after preprocessing) to yield reliable keyword extraction and were excluded from the NLP analysis, leaving 1,133 courses as the active NLP corpus.

Degree levels: 16 Bachelor programs (855 courses) and 9 Master programs (306 courses). YSU contributes the largest share (59.5% of courses), followed by AUA (21.4%), NUACA (15.0%), and RAU (4.1%).

### 5.2.2 Job Market Dataset

The job market side consists of a 1,369-posting broad market snapshot from 14 sources, collected in March 2026, and a downstream IT-only subset of 753 postings used for NLP extraction and alignment analysis.

**Table 5.2 — Job market dataset summary**

| Source | Type | Postings | Full text available |
|---|---|---|---|
| LinkedIn | Aggregator | 992 | Yes |
| SoftConstruct | Company portal | 152 | Yes |
| EPAM | Company portal | 108 | Yes |
| Staff.am | Aggregator | 55 | Yes |
| job.am | Aggregator | 20 | Yes |
| Grid Dynamics | Company portal | 11 | Yes |
| Krisp | Company portal | 7 | Yes |
| NVIDIA | Company portal | 5 | Yes |
| 10Web | Company portal | 5 | Yes |
| DataArt | Company portal | 5 | Yes |
| ServiceTitan | Company portal | 4 | Yes |
| Synopsys | Company portal | 2 | Yes |
| Picsart | Company portal | 2 | Yes |
| DISQO | Company portal | 1 | Yes |
| **Total (broad snapshot)** | | **1,369** | **100%** |

For downstream NLP and alignment analysis, the broad snapshot was narrowed to an IT-only subset of 753 postings. The 140 recurring boilerplate paragraphs (e.g., EPAM's standard "About Us" section appearing in 100+ postings) were stripped prior to skill extraction to prevent systematic inflation of company-generic terms.

---

## 5.3 Skill Extraction Results (Pre-ESCO Baseline)

### 5.3.1 Extraction Configuration

Two extraction methods were applied to both corpora using the same preprocessing pipeline:

- **TF-IDF:** ngram\_range=(1,3), max\_df=0.85, min\_df=2; 295 custom stopwords + 459 generic English unigrams + 11 multi-word noise phrases; top-10 terms per document
- **KeyBERT:** model=all-MiniLM-L6-v2 (22M parameters); use\_mmr=True, diversity=0.5; top\_n=10 per document

Post-extraction filters applied to both methods: company name blocklist (434 tokens), is\_skill\_like() filter rejecting tokens with >60% stop-word ratio and pure numeric/single-character strings.

### 5.3.2 Unique Skills Extracted

**Table 5.3 — Extracted skill vocabularies (post-filtering)**

| Corpus | TF-IDF unique skills | KeyBERT unique skills |
|---|---|---|
| Curriculum | 3,423 | 4,801 |
| Job market | 3,153 | 5,530 |

KeyBERT extracts more unique phrases than TF-IDF because it captures full multi-word semantic units rather than term-frequency peaks. Curriculum yields slightly more unique terms than the IT-only job corpus despite having a comparable document scale, reflecting the standardized vocabulary of academic course descriptions and the tighter job-scope definition after IT filtering.

### 5.3.3 Pre-ESCO Alignment Metrics

**Table 5.4 — Pre-ESCO string-level alignment (baseline)**

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Curriculum unique skills | 3,442 | 4,812 |
| Job market unique skills | 3,153 | 5,530 |
| **Overlap** | **279 (8.85%)** | **18 (0.33%)** |
| Gap (jobs demand, not taught) | 2,874 | 5,512 |
| Surplus (taught, not demanded) | 3,163 | 4,794 |

The overlap metric here is computed as the intersection of exact string matches between the curriculum skill set and the job market skill set, expressed as a proportion of the job market set. This pre-ESCO figure intentionally understates true alignment: synonymous phrases that describe identical competences (e.g., "object-oriented programming" vs. "OOP principles") count as non-overlapping until ESCO normalization is applied.

### 5.3.4 Divergence Between TF-IDF and KeyBERT Overlap

The difference in overlap rates between TF-IDF (8.85%) and KeyBERT (0.33%) is a structural artifact of the methods, not a finding about the true alignment. TF-IDF extracts individual words and short phrases that tend to be shared across all technical documents (e.g., `data`, `algorithms`, `analysis`). KeyBERT extracts idiomatic multi-word phrases anchored to each corpus's specific register:

- Curriculum phrases: `"object oriented programming"`, `"mathematical modeling applications"`, `"data structures algorithms"`
- Job market phrases: `"backend development experience"`, `"cloud infrastructure design"`, `"agile software delivery"`

These phrase pairs describe overlapping skills but share no common string. ESCO normalization resolves this by mapping both phrase types to shared concept identifiers.

### 5.3.5 Skills in the Overlap, Gap, and Surplus

**Skills in the overlap (present in both curricula and job market — TF-IDF):**

The 279 overlapping terms represent the most directly shared vocabulary. Representative examples include: `algorithms`, `analysis`, `data`, `design`, `machine learning`, `programming`, `python`, `statistics`, `testing`, `cloud`, `agile`, `software`, `networks`.

**Skills in the gap (demanded by employers, absent from curricula — TF-IDF top terms):**

| Rank | Skill | Job market frequency |
|---|---|---|
| 1 | docker | High |
| 2 | kubernetes | High |
| 3 | ci cd | High |
| 4 | devops | High |
| 5 | automation | High |
| 6 | backend | High |
| 7 | terraform | Medium |
| 8 | microservices | Medium |
| 9 | security | Medium |
| 10 | api | Medium |

These gap terms consistently appear across multiple employer types and sources, suggesting they represent genuine structural demand rather than company-specific preferences.

**Skills in the surplus (present in curricula, absent from job market — TF-IDF top terms):**

| Rank | Skill | Source |
|---|---|---|
| 1 | armenian language | YSU (multiple programs) |
| 2 | differential equations | YSU, NUACA |
| 3 | calculus | YSU, NUACA |
| 4 | philosophy | YSU (multiple programs) |
| 5 | history | YSU (multiple programs) |
| 6 | physics | YSU, NUACA |
| 7 | german language | YSU |
| 8 | french language | YSU |
| 9 | linear algebra | YSU, NUACA |
| 10 | physical education | YSU (multiple programs) |

The surplus includes two conceptually distinct categories: (1) general-education requirements mandated by the Armenian state educational standard (Armenian language, physical education, history, philosophy) that are not IT-specific competences; and (2) theoretical STEM content (calculus, differential equations, linear algebra, physics) that does not appear in job postings but may serve as a prerequisite foundation for advanced technical skills — its absence from job postings does not necessarily make it educationally irrelevant.

---

## 5.4 ESCO-Normalized Alignment Results

### 5.4.1 ESCO Threshold Calibration

The cosine similarity threshold for mapping extracted phrases to ESCO v1.2 concepts was calibrated empirically on a stratified set of 293 phrase–concept pairs (sampled across seven similarity bands from 0.50 to 1.00). Pairs were annotated as matches or non-matches using GPT-4o-mini as an automated judge (temperature=0), following the LLM-as-annotator approach established in recent NLP annotation research (Gilardi et al., 2023; He et al., 2024). A stratified 35-pair subset was independently reviewed by the author; agreement between the automated and human judgements was 94.3% (33/35 pairs), with two corrections applied before the threshold sweep.

A threshold sweep across 0.60–0.85 selected the threshold maximising F1 on the annotation sample:

**Table 5.5 — Threshold calibration results**

| Threshold | Precision | Recall | F1 | Coverage |
|---|---|---|---|---|
| 0.60 | 0.468 | 0.967 | 0.631 | 85.3% |
| 0.65 | 0.541 | 0.926 | 0.683 | 70.6% |
| 0.70 | 0.616 | 0.835 | 0.709 | 56.0% |
| **0.75** | **0.711** | **0.711** | **0.711** | **41.3%** |
| 0.80 | 0.833 | 0.537 | 0.653 | 26.6% |
| 0.85 | 0.907 | 0.322 | 0.476 | 14.7% |

The threshold of 0.75 was selected as it achieves the best F1 (0.711) with balanced precision and recall. A post-hoc sensitivity check confirmed that varying the threshold between 0.70 and 0.80 produces no change in the concept-level overlap count — additional phrase matches at lower thresholds map to ESCO concepts already represented at 0.75, confirming that the bottleneck is ESCO vocabulary coverage rather than threshold strictness.

### 5.4.2 Coverage After Normalization

**Table 5.6 — ESCO-normalized alignment results**

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Unique ESCO concepts in curriculum | 332 | 398 |
| Unique ESCO concepts in job market | 326 | 207 |
| **Overlap** | **107 (32.82%)** | **59 (28.5%)** |
| Gap (demanded, not taught) | 219 | 148 |
| Surplus (taught, not demanded) | 225 | 339 |

Coverage is expressed as the overlap divided by the number of unique job-market ESCO concepts. Both methods converge on the same overall story, with TF-IDF producing the stronger overlap on the IT-only analysis set.

The normalized results represent a substantial improvement over the pre-ESCO string baseline (TF-IDF: 8.85% → 32.82%; KeyBERT: 0.33% → 28.5%), demonstrating that ESCO normalization successfully resolves surface-form variation: phrase pairs such as "object oriented programming" and "OOP principles" now map to the same ESCO concept and count as overlap.

### 5.4.3 Knowledge vs. Applied Competence Split

ESCO v1.2 classifies each skill concept as either *knowledge* (declarative understanding of a subject) or *skill/competence* (ability to perform an action). Examining the overlap, gap, and surplus through this lens reveals a structural asymmetry:

**Table 5.7 — Knowledge vs. skill/competence distribution across alignment categories (TF-IDF)**

| Category | Knowledge | Skill/Competence | Total |
|---|---|---|---|
| Overlap (taught AND demanded) | 83 (77.6%) | 24 (22.4%) | 107 |
| Gap (demanded, NOT taught) | 107 (48.9%) | 112 (51.1%) | 219 |
| Surplus (taught, NOT demanded) | 136 (60.4%) | 88 (39.1%) | 225 |

The overlap is disproportionately composed of knowledge concepts (77.6%), while the gap remains slightly competence-heavy (51.1% skill/competence). This pattern indicates that Armenian IT curricula successfully cover the *knowledge* layer demanded by employers — subject matter familiarity with algorithms, data structures, programming languages, and technical domains — but fall short on the *applied competence* layer: the ability to perform specific technical tasks in commercial contexts (DevOps pipelines, responsive design, CI/CD workflows, cloud deployment). This distinction has implications for curriculum reform: the required changes are not primarily about what subject areas are taught, but about how they are practiced and assessed.

### 5.4.4 ESCO Vocabulary Coverage Limitation

Of the 19,998 unique extracted phrases submitted to ESCO matching, only 2,523 (12.6%) received an ESCO match above the 0.75 threshold. The remaining 17,475 phrases fall into two categories: (1) generic academic or job-posting language below any meaningful ESCO concept (e.g., "students will learn", "excellent communication"), and (2) specific modern technology terms not present in ESCO v1.2 (Docker, Kubernetes, React, Microsoft Azure, TypeScript, Node.js).

One confirmed false positive is `docker` mapping to the ESCO concept *dock operations* (a maritime logistics concept) at similarity 0.761 — a known embedding collision. This adds one spurious concept to the job-market set and slightly inflates the gap count, but does not affect the overlap.

The share of courses contributing zero ESCO concepts varies substantially by university, reflecting the description asymmetry documented in Section 5.6.1:

| University | Courses with 0 ESCO concepts |
|---|---|
| AUA | 30 / 248 (12%) |
| YSU | 184 / 691 (27%) |
| NUACA | 73 / 153 (48%) |
| RAU | 23 / 41 (56%) |

Nearly half of NUACA courses and more than half of RAU courses produce no ESCO concept assignment, meaning they contribute nothing to the alignment calculation. This structural dark matter further confirms that coverage figures for these institutions are lower bounds rather than true estimates.

The 32.82% overall TF-IDF coverage figure should be interpreted as a lower-bound estimate of true conceptual alignment within the ESCO-expressible vocabulary.

### 5.4.5 Emerging Tech Skills Beyond ESCO

A supplementary analysis using a curated technology lexicon (36 terms) identified modern tools absent from ESCO v1.2 and compared their presence across the two corpora:

**Table 5.7 — Emerging tech skills not in ESCO v1.2 (TF-IDF, by job market frequency)**

| Technology | Job postings | Curriculum courses | Status |
|---|---|---|---|
| Microsoft Azure | 35 | 0 | Gap |
| React | 30 | 0 | Gap |
| LLM / Generative AI | 25 | 4 | Overlap |
| Node.js | 20 | 3 | Overlap |
| Amazon Web Services | 20 | 0 | Gap |
| Go (Golang) | 14 | 0 | Gap |
| Microservices | 10 | 0 | Gap |
| REST API | 9 | 0 | Gap |
| Google Cloud | 8 | 0 | Gap |
| Kubernetes | 6 | 0 | Gap |
| Docker | 5 | 0 | Gap |

The dominant pattern is one-sided demand: the most-requested modern tools (Azure, React, AWS, Kubernetes, Docker) appear in job postings but not in any curriculum course content. LLM/GenAI is the only major emerging category with meaningful curriculum presence (4 courses), suggesting early but limited adoption.

### 5.4.6 Top Gap ESCO Skills (Demanded, Not Taught)

The 219 ESCO concepts in the TF-IDF gap span three analytically distinct categories:

**Technology skills:** PHP (2.7% of IT-only postings), Java (2.6%), TypeScript (2.3%), SQL Server (1.6%), DevOps (1.6%), CSS (1.3%), Android (1.3%), maintain responsive design (1.4%).

**Domain-specific skills (SoftConstruct effect):** betting, banking activities, gambling games, and related commercial concepts remain visible in the ESCO-based gap list. SoftConstruct contributes 37 postings to the IT-only analysis set, so these domain concepts are much smaller than in the original broad-market corpus but still require careful interpretation.

**Business and professional skills:** sales activities (4.0%), develop campaigns (1.4%), logistics (1.2%), comply with regulations (1.0%), contract law (0.9%), develop training programmes (0.8%). These reflect the operational context of IT roles in commercial environments.

### 5.4.7 Top Surplus ESCO Skills (Taught, Not Demanded)

The 225 ESCO surplus concepts divide into three categories:

**General-education requirements** mandated by Armenian state educational standards: these include language courses (Chinese, Turkish, Ancient Greek), humanities (Christianity, acting techniques), and physical/life sciences outside the IT domain. These are not misalignments in the pedagogical sense — they fulfil accreditation requirements and are not expected to appear in IT job postings.

**Advanced theoretical content:** algebra, Monte Carlo simulation, biostatistics, artificial neural networks, aerospace engineering, analyse scientific data. These represent graduate-level analytical foundations whose market relevance is not directly signalled by job posting language but may underpin applied competences that are demanded.

**Niche technical tools:** MATLAB, Assembly language, Capture One (photo editing), Iterative development. These appear in curricula but are not represented in the Armenian IT job market sample.

---

## 5.5 Per-University and Per-Program Results

### 5.5.1 University-Level Alignment Scores

**Table 5.8 — Alignment by university (TF-IDF, ESCO-normalized)**

| University | Programs | Avg. coverage | Total ESCO concepts | Notes |
|---|---|---|---|---|
| AUA | 7 | 8.06% | 387 | Full descriptions; most reliable |
| YSU | 14 | 5.96% | 679 | Full descriptions (translated); largest dataset |
| RAU | 1 | 2.76% | 18 | Single program; high uncertainty |
| NUACA | 5 | 2.52% | 68 | Course names only; lower bound |

AUA achieves the highest average alignment (8.06%), consistent with its richer course description availability and English-language instruction. YSU ranks second at 5.96%. NUACA and RAU remain substantially lower, reflecting the description asymmetry documented in Section 5.6.1 — name-only analysis structurally underestimates skill content.

Coverage percentages are expressed as the fraction of all unique job-market ESCO concepts covered by each university's programs. The denominator (326 concepts in TF-IDF) still includes some domain-specific concepts from employer-specific postings, so the figures remain conservative estimates.

### 5.5.2 Program-Level Alignment Scores

**Table 5.9 — Per-program coverage (TF-IDF, ESCO-normalized, ranked)**

| Rank | University | Program | Degree | Coverage |
|---|---|---|---|---|
| 1 | AUA | Computer and Information Science | Master | 12.27% |
| 2 | AUA | Computer Science | Bachelor | 10.74% |
| 3 | AUA | Data Science | Bachelor | 8.28% |
| 4 | YSU | Data Science in Business | Master | 7.98% |
| 5 | YSU | Information Systems Development | Master | 7.98% |
| 6 | AUA | General Education | General | 7.67% |
| 7 | AUA | Industrial Engineering and Systems Management | Master | 7.06% |
| 8 | YSU | Applied Statistics and Data Science | Bachelor | 6.75% |
| 9 | YSU | Applied Statistics and Data Science | Master | 6.44% |
| 10 | YSU | Information Systems Management | Master | 6.13% |
| … | | | | |
| 25 | NUACA | Geographic Information Systems | Master | 0.92% |

The spread between the best program (AUA CIS, 12.27%) and worst (NUACA GIS, 0.92%) is substantial, indicating major variation in how well individual programs prepare students for market-demanded skills. AUA programs occupy the top three positions. Data Science and Applied Statistics programs from both AUA and YSU cluster in the top half, reflecting stronger overlap between quantitative analytical curricula and market demand. NUACA programs occupy the bottom range, consistent with the description asymmetry limitation.

### 5.5.3 Bachelor vs. Master Degree Comparison

**Table 5.10 — Alignment by degree level (TF-IDF)**

| Degree | Programs | Avg. coverage |
|---|---|---|
| Master | 13 | 5.66% |
| Bachelor | 13 | 5.69% |
| General | 1 | 7.67% |

Bachelor and Master programs show nearly identical average coverage (5.69% vs. 5.66%), indicating that degree level is not a meaningful predictor of curriculum–market alignment in this sample. The tiny difference reinforces that the gap is driven more by curriculum design priorities than by degree level.

---

## 5.6 Sensitivity Analyses

Three sensitivity analyses were conducted to assess the robustness of the extraction results. Full details are documented in `docs/sensitivity_analysis.md` and `notebooks/3_analysis/03_sensitivity_analysis.ipynb`.

### 5.6.1 Description Asymmetry (AUA Sensitivity Test)

The impact of description availability on alignment detection was quantified by running the TF-IDF extraction on AUA data twice: once using only course names (as is the case for NUACA and most YSU courses) and once using full course descriptions.

**Table 5.7 — AUA description asymmetry test results**

| Input | AUA–job overlap rate |
|---|---|
| Course names only | 1.3% |
| Course names + full descriptions | 6.8% |

The 5× difference demonstrates that name-only analysis severely underestimates the true skill content of a program. This finding implies that the alignment scores for YSU (name + translated description available but shorter than AUA), NUACA (name only), and RAU (name only) should be interpreted as lower bounds. AUA's results are the most reliable cross-institutional benchmark.

### 5.6.2 Validation Against Human-Curated Skill Tags

A subset of 151 job postings (104 EPAM, 47 Staff.am) carried human-curated `skills_tags` fields populated by the hiring companies or platform editors. These tags were used as ground-truth proxies to evaluate extraction quality.

**Table 5.8 — Recall against human-curated skill tags**

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Jobs with ≥1 tag matched (soft/exact) | 64.2% / 45.7% | 38.4% / 19.2% |
| Macro avg. recall per job (soft) | 44% | 21% |
| Macro avg. recall per job (exact) | 28% | 11% |

TF-IDF outperforms KeyBERT on this validation because `skills_tags` fields typically contain individual technology names (e.g., `Python`, `React`, `AWS`) that match TF-IDF unigrams more directly than KeyBERT's longer semantic phrases.

The 44% soft recall of TF-IDF indicates that approximately half of human-identified skills are retrieved; the remaining skills either (a) are not mentioned in the job text body at all, (b) appear only in skill tag metadata, or (c) use phrasing that falls below the extraction filters. This recall level is consistent with unsupervised extraction benchmarks in the literature (e.g., Ahadi et al., 2022 report comparable figures for TF-IDF on curriculum data).

### 5.6.3 Noise Audit

Prior to the noise cleanup described in Section 4.5.6, an audit of the 584 TF-IDF overlapping terms found that 351 (60%) were generic English words with no specific IT skill meaning (e.g., `"team"`, `"experience"`, `"role"`, `"environment"`). Following the addition of 459 generic unigrams and 11 noise phrases to the extraction filters, and then rerunning the analysis on the IT-only job subset, the overlap was revised to 279 — a reduction that improved the precision of the reported alignment rate from an inflated 12.6% to a more conservative and defensible 8.85%.

This audit is reported here as a finding because it quantifies the magnitude of noise in unsupervised extraction and demonstrates the importance of systematic quality control. The cleaned 8.85% figure is used in all subsequent analyses.

---

## 5.7 Summary of Results

**Pre-ESCO baseline:** String-level overlap is low (TF-IDF 8.85%, KeyBERT 0.33%), as expected — synonymous phrases describing the same skill are counted as non-overlapping until normalization is applied.

**ESCO-normalized alignment:** After mapping extracted phrases to shared ESCO concept identifiers, coverage rises to 32.82% (TF-IDF) and 28.5% (KeyBERT). Both estimates remain well above the string-level baseline, confirming the value of normalization.

**Knowledge vs. competence:** The overlap is 77.6% *knowledge* concepts (shared factual domains) and 22.4% *skill/competence*. The gap is 51.1% applied competences. Curricula cover the knowledge layer but fall short on applied practice — DevOps, CI/CD, cloud deployment, responsive design.

**Gap pattern:** The skill gap is concentrated in three clusters: (1) modern cloud and DevOps tooling (Azure, React, AWS, Docker, Kubernetes, Terraform — all absent from curricula); (2) domain-specific competences driven by the gaming/betting industry (SoftConstruct effect); and (3) practical software delivery skills (CI/CD, microservices, REST APIs).

**Surplus pattern:** The surplus consists primarily of general-education requirements mandated by state standards (languages, humanities, physical education) and advanced theoretical content (algebra, Monte Carlo simulation, biostatistics) whose market relevance is not directly signalled by job posting language.

**Per-program variation:** Coverage ranges from 12.27% (AUA Computer and Information Science, Master) to 0.92% (NUACA GIS, Master). AUA consistently outperforms due to richer description availability. Degree level (Bachelor vs. Master) is not a meaningful predictor of alignment.

**Key limitation:** The 32.82% coverage figure is a lower bound. ESCO v1.2 does not contain Docker, Kubernetes, React, Azure, and other modern tools — these are captured separately in the emerging skills analysis. Adjusting for ESCO's vocabulary gap, true conceptual alignment is likely higher.

The sensitivity analyses confirm that: (a) programs with richer description data produce substantially higher alignment estimates; (b) roughly 44% of human-identified skills in job postings are recoverable by TF-IDF extraction; and (c) noise filtering is essential for interpretable results.

---

*Citation checklist for this chapter:*
- *Ahadi et al. (2022) — EDM 2022, for soft recall comparison — verified ✓*
