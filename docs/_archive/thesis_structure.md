# Thesis Structure

*For: Master's Thesis — Alignment between Armenian University IT/STEM Curricula and Labor Market Skill Demand*
*Purpose: Skeleton and writing guide — not draft prose*
*Standard followed: European Bologna-aligned computational thesis + STEM/data-science conventions*
*Last updated: 2026-03-22*

---

## Front Matter (non-negotiable academic components)

- Title page (university, department, author, supervisor, year)
- Abstract (~250–350 words): problem, data, method, key findings, conclusion
- Acknowledgments (optional but common)
- Table of Contents
- List of Figures / List of Tables
- List of Abbreviations (ESCO, NLP, YSU, AUA, etc.)

---

## Chapter 1 — Introduction

**Target length:** ~1,500–2,000 words

### 1.1 Background and Motivation
- Global context: rapid change in IT skill demands (WEF 2025 — 40% of skills disrupted in 5 years)
- Why curriculum alignment matters: graduates lack demanded skills even with relevant degrees
- Armenia-specific case: IT sector reports unfilled vacancies despite high graduate numbers (Kupets 2016)
- Why this gap persists: Soviet-era path dependency in higher education structure

### 1.2 Research Gap
- Most alignment studies focus on: US, EU, Middle East (Saudi Arabia, Azerbaijan)
- Armenian and post-Soviet IT education largely absent from computational alignment research
- No prior data-driven, multi-source study of this kind for Armenia

### 1.3 Research Questions
- **RQ1:** What skills do Armenian IT universities teach, and what skills does the Armenian IT labor market demand?
- **RQ2:** Is there a measurable gap between the two, and how large is it?
- **RQ3:** Which programs and universities show stronger or weaker alignment?
- **RQ4:** What categories of skills are systematically missing from curricula?

### 1.4 Thesis Scope and Structure
- Scope: 4 universities, 26 programs, 1,161 courses; 11 job data sources, 1,348 postings; snapshot of March 2026
- Explicitly out of scope: NPUA (data inaccessible), longitudinal trends, salary analysis
- Brief overview of chapter structure (1 sentence per chapter)

---

## Chapter 2 — Literature Review

**Target length:** ~4,000–6,000 words

### 2.1 Curriculum–Labor Market Alignment: Overview
- Define the problem domain: skill mismatch vs. overeducation — two distinct failure modes
- Cite: Aljohani et al. (2022) systematic review — confirms active research area, maps methodological clusters
- Note the regional gap: post-Soviet/Central Asian systems underrepresented in literature

### 2.2 Computational Approaches to Curriculum Alignment
- Early work: keyword matching, TF-IDF-based overlap
- More recent: NLP-based extraction + taxonomy normalization (Almaleh et al. 2019 as primary precedent)
- Emerging: transformer-based embeddings for semantic matching
- Cite: Almaleh et al. (2019) — closest methodological precedent; Saudi Arabia context, Naive Bayes + cosine similarity
- Cite: EDM 2022 "Skills Taught vs Skills Sought" — parallel framing ⚠️ verify authors before citing
- Cite: Musazade et al. (2025) UniSkill dataset — near-parallel concurrent work ⚠️ check venue

### 2.3 NLP for Skill Extraction
- Skill extraction as a subtask of information extraction / named entity recognition
- Two paradigms: unsupervised (KeyBERT, TF-IDF) vs. supervised (SkillSpan NER, fine-tuned transformers)
- Cite: Zhang et al. (2022) SkillSpan — best current supervised method for English job ads
- Cite: Reimers & Gurevych (2019) Sentence-BERT — foundational sentence embedding method
- Multilingual challenge: Armenian text requires translation or multilingual models

### 2.4 Skill Taxonomies as Measurement Instruments
- Why a shared taxonomy is needed: raw extracted phrases are noisy, unshareable, not comparable
- ESCO: EU multilingual taxonomy, designed for education-employment interface (primary choice)
- O*NET: US occupational taxonomy, useful as secondary cross-reference
- SFIA: IT-specific professional framework, useful for interpreting skill *level* not just presence
- Cite: Chiarello et al. (2021) on ESCO coverage gaps for Industry 4.0 skills
- Cite: Autor, Levy & Murnane (2003) — foundational framework for why skills are task-based (theoretical anchor)

### 2.5 Armenia and Post-Soviet Higher Education Context
- Bologna Process adoption and its structural impact on Armenian universities
- IT sector growth in Armenia: diaspora investment, tech company expansion (Picsart, Krisp, EPAM, SoftConstruct)
- Evidence for skill mismatch: Kupets (2016) — ~30% overeducated, 69.9% report education has limited usefulness
- Regional comparator: Amirova & Valiyev (2021) Azerbaijan — employers and graduates disagree on which competences matter

### 2.6 Constructive Alignment Theory (Conceptual Framework Anchor)
- Biggs & Tang (2011): internal curriculum coherence — ILOs, teaching activities, assessment aligned
- Extension to external alignment: same logic applies to labor market outcomes
- If ILOs are vague or absent (as in many post-Soviet course descriptions), the gap is structural
- This thesis measures the distance between implicit ILOs (in course names/descriptions) and explicit employer demands

---

## Chapter 3 — Theoretical Framework

**Target length:** ~1,500–2,500 words
*(can be merged with Literature Review if supervisor prefers; keep separate for stronger academic structure)*

### 3.1 Constructive Alignment (Biggs & Tang 2011)
- ILOs as the bridge between curriculum and competence measurement
- Applying external alignment logic: labor market = external benchmark for ILO relevance
- Why the framework justifies the computational approach

### 3.2 Task-Based View of Skills (Autor, Levy & Murnane 2003)
- Skills are defined by what tasks they enable — not abstract categories
- Justifies using job postings as skill proxies: they describe tasks employers need done
- Underpins the choice to use a skill taxonomy (ESCO) rather than free-form labels

### 3.3 ESCO as the Operationalization Layer
- Translates abstract skills into measurable taxonomy concepts
- Justified for Armenia: Bologna Process alignment, multilingual coverage, open API
- Limitations acknowledged: 2–3 year taxonomy lag for emerging tech skills

---

## Chapter 4 — Methodology

**Target length:** ~3,500–5,000 words
*(this is the most critical chapter for a computational thesis — be thorough)*

### 4.1 Research Design
- Quantitative, data-driven comparative corpus study (cross-sectional snapshot)
- Not a survey, not an experiment — corpus analysis of two text corpora
- Justification for computational approach vs. survey: reproducibility, scale, transparency (see Section 6.4 of research_foundation.md)
- Two-phase: (1) skill extraction from text, (2) alignment gap analysis

### 4.2 Curriculum Dataset
- Sources: YSU (web scrape via Apify), AUA (web scrape), NUACA (web scrape), RAU (PDF parsing)
- Final dataset: 1,161 courses, 26 programs, 4 universities, 2 degree levels
- Schema: 18 columns including course_name, description, credits, degree_level, program_name, source_language
- Language: YSU (Armenian, 691 rows), AUA (English, 249), NUACA (English, 174), RAU (Russian→English, 47)
- Quality flags: 129 YSU duplicates removed; AUA has richest descriptions; RAU limited to 1 program
- File: `data/processed/university/final_curriculum_dataset.csv`

### 4.3 Job Market Dataset
- 11 sources: LinkedIn (992), SoftConstruct (152), EPAM (108), Staff.am (55), job.am (20), Krisp (7), DataArt (5), ServiceTitan (4), Synopsys (2), Picsart (2), DISQO (1)
- Total: 1,348 postings; all from Armenia/Yerevan as of March 2026
- Source types: aggregators (LinkedIn, Staff.am, job.am) vs. company portals (8 direct employers)
- Schema: 13 columns including full_text, source_type, seniority_level, employment_type, skills_tags
- `full_text` coverage: 100% (key field for NLP extraction)
- File: `data/processed/jobs/final_jobs_dataset.csv`

### 4.4 Data Limitations
- NPUA excluded (HTTP 403 + Cloudflare blocking — largest technical university in Armenia)
- RAU partial coverage: 1 of ~8 IT programs
- UFAR not assessed (French-language institution, out of scope)
- Job data: snapshot in time (March 2026), company portal sample small (281 rows)
- AUA-only rich descriptions: other universities provide course names only
- Refer to: `docs/data_gaps_and_limitations.md` for full documentation

### 4.5 NLP Pipeline — Skill Extraction
- Step 1: YSU translation — Helsinki-NLP/opus-mt-hy-en (or Google Translate API); validate on 50-row sample
- Step 2: Curriculum skill extraction — KeyBERT with `paraphrase-multilingual-mpnet-base-v2`; 3–7 phrases per course
- Step 3: Job skill extraction — KeyBERT on `full_text`; optionally SkillSpan NER for English postings
- Step 4: ESCO normalization — cosine similarity against ESCO v1.2 skill descriptions; threshold ≥ 0.75
- Step 5: Residual "emerging skills" — unmatched high-frequency phrases kept as separate finding

### 4.6 Alignment Analysis
- Coverage rate = |curriculum_skills ∩ job_skills| / |job_skills|
- Gap set = job skills not present in any curriculum skill inventory
- Surplus set = curriculum skills not demanded by any job posting
- Computed at: overall, per university, per program, Bachelor vs. Master
- Optional: source_type weighting (company_portal rows weighted higher as direct employer demand)

### 4.7 Evaluation
- No gold-standard labels available — unsupervised pipeline
- Validation strategy: manual inspection of 50-row extraction sample; inter-rater agreement on skill label assignment (if two reviewers used)
- Baseline comparison: simple TF-IDF keyword overlap vs. ESCO-normalized coverage rate

---

## Chapter 5 — Results

**Target length:** ~3,000–4,500 words
*(let data speak — minimal narrative in this chapter)*

### 5.1 Skill Inventory Overview
- Total unique ESCO skills extracted from curricula (N)
- Total unique ESCO skills extracted from job postings (N)
- Top-20 skills by frequency: curricula vs. jobs (side-by-side table)
- Distribution of emerging (unmatched) skills — separate table

### 5.2 Overall Alignment Metrics
- Overall curriculum coverage rate: X%
- Overall gap count (job skills missing from curricula): N unique skills
- Overall surplus count (curriculum skills not demanded): N unique skills
- Summary table: coverage rate by university (4 rows)

### 5.3 Per-University Findings
- Coverage rate per university (table + bar chart)
- Top-10 gap skills per university
- Comparison: which university has strongest/weakest alignment
- Degree level breakdown: Bachelor vs. Master coverage rates

### 5.4 Per-Program Findings
- Heatmap: 26 programs × top-50 ESCO skills (presence/absence, 0/1)
- Programs with highest and lowest alignment scores
- Programs with unusual surplus (curriculum-only skills not found in any job)

### 5.5 Skill Gap Analysis
- Top-20 most demanded skills completely absent from all curricula (gap skills)
- Categorize by ESCO skill type: technical (ICT), cognitive, social/interpersonal
- Emerging skills not in ESCO: list with frequency counts from job data

### 5.6 Source-Type Analysis (aggregators vs. company portals)
- Coverage rate: aggregator job postings vs. company portal postings
- Skill frequency comparison: what do direct employers demand more vs. aggregator-listed jobs?
- Note: company portal sample is small (N=281) — report with appropriate caution

---

## Chapter 6 — Discussion

**Target length:** ~2,500–4,000 words

### 6.1 Interpretation of Key Findings
- What the gap means in context: specific skill categories systematically missing
- Whether Bachelor vs. Master programs differ and why
- University-level variation: what explains differences in alignment (e.g., AUA's richer descriptions may inflate measured coverage; YSU's scale vs. curriculum rigidity)

### 6.2 Comparison to Related Work
- Compare coverage rate to Almaleh et al. (2019): their Saudi Arabia findings vs. Armenia
- Compare identified gap skills to Kupets (2016): do computational findings confirm survey evidence?
- Compare university variation patterns to Amirova & Valiyev (2021): Azerbaijan patterns vs. Armenia

### 6.3 Implications for Curriculum Design
- Which skills should be added (high-frequency gap skills)
- Which programs are closest to being market-aligned (best-practice examples)
- Constructive alignment lens: are the ILO-gaps topic gaps or depth gaps? (if Bloom's analysis done)
- Policy implications: for university curriculum committees, accreditation bodies (ANQA)

### 6.4 Limitations
- Data coverage: NPUA absent, RAU partial, UFAR not assessed — findings reflect ~50% of Armenian IT programs
- Time snapshot: March 2026 only; labor market is dynamic
- NLP precision: KeyBERT extracts salient phrases, not verified skills; ESCO lag for emerging tech
- AUA advantage: richer descriptions may overstate curriculum coverage vs. other universities
- Company portal sample too small for company-level conclusions

### 6.5 Future Work
- Extend to NPUA (via direct institutional contact or ANQA accreditation documents)
- Longitudinal study: repeat analysis in 2027–2028 to detect curriculum update response
- Expert validation: survey 10–15 Armenian IT employers to validate top-N gap findings
- Predictive model: train classifier to forecast alignment trajectories

---

## Chapter 7 — Conclusion

**Target length:** ~800–1,200 words

### 7.1 Summary of Findings
- Restate RQ1–RQ4 and answer each in 1–2 sentences
- State the overall alignment/gap figure

### 7.2 Contribution
- First computational curriculum–job market alignment study for Armenian IT education
- Multi-source job dataset (11 sources) — more diverse than most prior work
- Reproducible pipeline documented and archived

### 7.3 Practical Recommendations
- For universities: specific programs to prioritize for curriculum review
- For accreditation bodies: ESCO-normalized gap metrics as a monitoring tool
- For students: skill areas to self-supplement beyond curriculum

---

## Back Matter

- **References** — APA 7th edition (or check supervisor requirement)
  - Minimum: Almaleh 2019, Aljohani 2022, Kupets 2016, Amirova & Valiyev 2021, WEF 2025, Biggs & Tang 2011, Autor et al. 2003, Zhang et al. 2022, ESCO documentation, KeyBERT (Grootendorst 2020)
- **Appendix A** — Data collection sources (all 11 job sources + 4 universities, with URLs and row counts)
- **Appendix B** — Scraping methods summary (refer to `docs/scraping_methods_log.md`)
- **Appendix C** — Full ESCO skill gap table (if too long for main text)
- **Appendix D** — YSU translation validation sample (50 rows with original Armenian + translation)
- **Appendix E** — Per-program coverage scores (full table)

---

## Estimated Total Length

| Chapter | Target words |
|---|---|
| Front Matter | ~500 |
| Ch. 1 Introduction | 1,500–2,000 |
| Ch. 2 Literature Review | 4,000–6,000 |
| Ch. 3 Theoretical Framework | 1,500–2,500 |
| Ch. 4 Methodology | 3,500–5,000 |
| Ch. 5 Results | 3,000–4,500 |
| Ch. 6 Discussion | 2,500–4,000 |
| Ch. 7 Conclusion | 800–1,200 |
| Back Matter / Appendices | ~1,000–2,000 |
| **Total** | **~18,300–27,700 words** |

*Typical range for a 30-ECTS European master's thesis: 15,000–25,000 words. This is within scope.*

---

## Gaps to Address Before Final Thesis Writing

These are items that are not yet complete but are needed for specific thesis sections. Listed in priority order.

---

### CRITICAL — must be done before writing

**1. Complete Phase 3: Skill Extraction (Phase 3 pipeline)**
- Without extraction results, Chapters 5 and 6 cannot be written
- Decisions needed first (see `docs/research_foundation.md` Section 7):
  - YSU translation method (Helsinki-NLP vs. Google Translate)
  - Skill extraction method (KeyBERT / SkillSpan / ESCO API)
  - ESCO normalization threshold

**2. Verify partially-verified citations (⚠️ items in research_foundation.md)**
- EDM 2022 paper — retrieve author names from proceedings
- Musazade et al. (2025) arXiv 2603.03134 — check if accepted to a venue
- Grootendorst (2020) KeyBERT — confirm publication details for reference list

**3. Confirm thesis format requirements with supervisor/department**
- Word count requirement (30 ECTS or 60 ECTS?)
- Citation style (APA 7 / IEEE / other?)
- Required sections (is a separate Theoretical Framework chapter required, or merged with Lit Review?)
- Language of thesis (English assumed, but confirm)

---

### IMPORTANT — needed for methodology and results quality

**4. Establish a validation strategy for skill extraction**
- Without at least a manual sample check, the methodology chapter will be weak
- Minimum: manually inspect 50 extracted skills from job data + 50 from curriculum data
- Write down the inspection results — this becomes a paragraph in Section 4.7

**5. Run the translation pipeline on YSU courses and validate quality**
- Need a sample of 50 Armenian → English translations reviewed before full pipeline run
- This is required to justify the chosen translation method in Section 4.5

**6. Decide on Bloom's taxonomy classification**
- Low effort (lookup table of ~50 verbs), adds a methodologically distinctive layer
- If yes: add to pipeline; add subsection 4.5.x and results subsection 5.x
- If no: remove references to it from this document and from research_foundation.md

---

### USEFUL — strengthens discussion and context chapters

**7. Find exact program-level enrollment or student count data for Armenian universities**
- Useful for framing the scale of the gap (how many students are affected?)
- Source: ANQA annual reports, UNESCO Institute for Statistics, Armenian Statistical Service (armstat.am)

**8. Check if ANQA publishes curriculum accreditation criteria publicly**
- If yes: adds a policy-level reference point for the discussion chapter
- Site: https://anqa.am

**9. Optional: find one comparison data point from a non-post-Soviet EU country**
- E.g., a study measuring ESCO curriculum coverage for a Polish or Czech IT program
- Would make the Discussion section internationally comparable, not just Armenia vs. Azerbaijan

---

### OPTIONAL — only if time permits

**10. Expert validation survey**
- 5–10 Armenian IT professionals rating the top-10 identified gap skills
- Adds qualitative triangulation; supervisor may require it
- Decision: skip unless supervisor specifically requests it (see research_foundation.md Section 6)

**11. Bloom's cognitive depth analysis**
- Classify curriculum course ILO verbs by Bloom level (Remember → Create)
- Compare Bloom levels of curricula vs. implied task complexity in job descriptions
- Adds a depth-vs-topic dimension to the gap analysis

---

*Cross-reference files:*
- `docs/research_foundation.md` — literature, taxonomy detail, analysis options, risks
- `docs/data_gaps_and_limitations.md` — dataset limitations for Chapter 4.4 and Chapter 6.4
- `docs/data_processing_pipeline.md` — curriculum dataset technical detail for Chapter 4.2
- `docs/jobs_data_pipeline.md` — job dataset technical detail for Chapter 4.3
- `docs/scraping_methods_log.md` — scraping decisions for Appendix B

*Last updated: 2026-03-22*
