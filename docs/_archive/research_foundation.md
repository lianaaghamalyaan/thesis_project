# Research Foundation

*For: Master's Thesis — Alignment between Armenian University IT/STEM Curricula and Labor Market Skill Demand*
*Purpose: Working research notes to support thesis writing — not draft prose*
*Last updated: 2026-03-22*

> **Note on citations:** Sources marked ⚠️ were partially verified (arXiv preprints or IEEE pages without full author retrieval). Verify authors before including in the final thesis bibliography.

---

## 1. Related Literature

### 1.1 The Curriculum–Labor Market Gap Problem

The core problem this thesis addresses is well-established in the literature: universities produce graduates whose skill profiles do not match what employers need. The gap manifests as two simultaneous failures — overeducation (workers holding credentials beyond job requirements) and skill mismatch (workers lacking specific technical skills despite holding relevant degrees).

---

**Almaleh, A., Aslam, M. A., Saeedi, K., & Aljohani, N. R. (2019).** "Align My Curriculum: A Framework to Bridge the Gap between Acquired University Curriculum and Required Market Skills." *Sustainability*, 11(9), 2607. MDPI. https://doi.org/10.3390/su11092607

*What it does:* Proposes a data-driven framework using Naive Bayes classification and cosine similarity to compare job postings against university course syllabi. Tests this on computing faculties in Saudi Arabia.

*Why it matters for this thesis:* This is the closest methodological precedent. The paper uses a two-dataset approach (curricula + job ads) and quantifies the gap computationally — exactly the approach taken here. Key differences: (1) their curricula data comes from syllabi text, ours comes from course names and descriptions; (2) their job ads are from a single Saudi portal, ours span 11 sources; (3) they use Naive Bayes + cosine similarity while we will likely use transformer embeddings. Use this as the primary prior work reference.

---

**Aljohani, N., et al. (2022).** "Bridging the skill gap between the acquired university curriculum and the requirements of the job market: A data-driven analysis of scientific literature." *Journal of Innovation & Knowledge* (Elsevier). https://www.sciencedirect.com/science/article/pii/S2444569X22000300

*What it does:* Systematic review of 10,214 Scopus records (2010–2021) on curriculum alignment. Maps the research landscape, identifies which industries and regions are most studied.

*Why it matters:* Useful for the literature review section — confirms this is an active research area, names the major methodological clusters, and can be cited to show the broader context. Also useful for noting what's *missing* in the literature: Central Asian and post-Soviet education systems are largely absent from this body of work, which strengthens the originality argument for this thesis.

---

⚠️ **Unknown authors (2022).** "Skills Taught vs Skills Sought: Using Skills Analytics to Identify the Gaps between Curriculum and Job Markets." *Proceedings of the 15th International Conference on Educational Data Mining (EDM 2022)*. https://educationaldatamining.org/edm2022/proceedings/2022.EDM-posters.56/

*What it does:* Uses analytics on both curriculum documents and job postings to identify skill gaps in a data-driven way. Conference paper format — likely methodologically concise.

*Why it matters:* The title exactly parallels the framing of this thesis. If the methodology is compatible, this could be cited as a direct precedent. **Action needed:** Open the EDM 2022 proceedings page to retrieve author names before citing.

---

### 1.2 The Armenian and Post-Soviet Context

**Kupets, O. (2016).** "Skill Mismatch and Overeducation in Transition Economies." *IZA World of Labor*, Article 224. https://wol.iza.org/articles/skill-mismatch-and-overeducation-in-transition-economies/long

*What it does:* Synthesizes empirical evidence on skill mismatch across former Soviet and Eastern European economies, drawing on World Bank STEP survey data. Armenia is included in the empirical base.

*Key findings relevant to Armenia:*
- ~30% of urban workers in Armenia are overeducated for their current jobs
- 69.9% of overeducated Armenian workers report their formal education has limited usefulness for their current work
- The IT sector in Armenia specifically reports thousands of unfilled vacancies despite high graduate unemployment
- Mismatch is structural (system-level, not just individual), reflecting Soviet-era educational path dependency

*Why it matters:* This is the most directly relevant empirical source for the thesis context. Cite in Chapter 1 (Introduction) and Chapter 3 (Context). The Armenia-specific data points are thesis-grade supporting evidence for the "why does this matter" argument.

*(Also see: Kupets, O. (2015). "Education in Transition and Job Mismatch: Evidence from the Skills Survey in Non-EU Transition Economies." KIER Working Paper No. 915, Kyoto University. https://ideas.repec.org/p/kyo/wpaper/915.html — earlier working paper version of the same research.)*

---

**Amirova, G., & Valiyev, A. (2021).** "Do University Graduate Competences Match Post-Socialist Labour Market Demands? Evidence from Azerbaijan." *Journal of Teaching and Learning for Graduate Employability*, 12(2), 332–347. https://ojs.deakin.edu.au/index.php/jtlge/article/view/1048

*What it does:* Studies the gap between graduate competences and employer expectations in Azerbaijan — former Soviet country with close structural and cultural similarity to Armenia. Surveys employers and graduates on 24 transferable and technical skills.

*Why it matters:* The Azerbaijani context is the closest published academic study geographically and institutionally to this thesis. Both countries share: post-Soviet higher education structure, Bologna Process adoption path, similar IT sector emergence dynamics, and small domestic market size. Use this as a regional comparator. Key finding: employers and graduates sharply disagree on which competences are most important — employers value practical technical skills and communication, graduates overestimate formal knowledge credentials.

---

**World Economic Forum. (2025).** *The Future of Jobs Report 2025.* World Economic Forum. https://www.weforum.org/publications/the-future-of-jobs-report-2025/

*What it does:* Surveys 1,000+ major employers across 55 economies on projected skill disruption through 2030. Identifies fastest-growing and fastest-declining skills globally.

*Key findings for framing:*
- Technology skills (AI, big data, cybersecurity, programming) are the top-growing demand area
- ~40% of existing job skills will be disrupted within 5 years
- Analytical thinking + creative thinking remain most valued across sectors
- Problem-solving, adaptability, and cross-functional technical literacy are growing

*Why it matters:* Use in the Introduction to frame the global urgency of curriculum alignment. The 2025 edition is the most current. This is not a methodological source — it's contextual and motivational. Cite as an institutional report, not a peer-reviewed paper.

---

### 1.3 Curriculum Design Theory

**Biggs, J., & Tang, C. (2011).** *Teaching for Quality Learning at University* (4th ed.). Open University Press. ISBN: 9780335242757.

*What it does:* Introduces and elaborates **constructive alignment** — the principle that learning outcomes, teaching/learning activities, and assessment tasks must be internally consistent and aligned with each other.

*Why it matters:* Provides the theoretical framework for *why* curriculum–job market alignment matters from a pedagogical standpoint. Constructive alignment was designed for internal coherence, but the same logic extends to external alignment with labor market outcomes. When this thesis argues that course X doesn't produce skill Y that employers need, the Biggs & Tang framework explains what a properly aligned curriculum would look like. Cite in the theoretical framework section of Chapter 2.

*Key concept to use:* "Intended learning outcomes" (ILOs) are the bridge between curriculum design and competence measurement — if ILOs are vague or misaligned with market demands, the gap is structural. This thesis is in part measuring the distance between the *implicit* ILOs encoded in course names/descriptions and the explicit skill demands of employers.

---

### 1.4 Task-Based Analysis of Skills (foundational economics background)

**Autor, D. H., Levy, F., & Murnane, R. J. (2003).** "The Skill Content of Recent Technological Change: An Empirical Exploration." *The Quarterly Journal of Economics*, 118(4), 1279–1333. Oxford University Press. https://doi.org/10.1093/qje/118.4.1279

*What it does:* Uses O*NET task data to classify occupations by cognitive/manual and routine/non-routine task content. Shows that technology substitutes for routine tasks and complements non-routine cognitive tasks.

*Why it matters:* This is foundational labor economics that your thesis builds on conceptually. It establishes why skill taxonomies (O*NET, ESCO) matter — they encode what tasks a job requires, which is what skill extraction is trying to measure. The framework is implicitly present whenever you classify job skills as "technical/hard" vs. "soft/interpersonal" or as "routine/automatable" vs. "judgment-based."

*Note:* This paper is widely cited but not directly applied in your methodology. Use it in the theoretical background (Chapter 2) to explain why skill taxonomies are a valid measurement instrument, not just a convenience.

---

## 2. Skill Taxonomies and Alignment Frameworks

### 2.1 ESCO — European Skills, Competences, Qualifications and Occupations

**Source:** European Commission, https://esco.ec.europa.eu/en/about-esco/what-esco

**What ESCO is:**
- Multilingual EU taxonomy: 3,039 occupations, 13,939 skills/competences, in 28 languages
- Structured as a three-pillar ontology: Occupations ↔ Skills/Competences ↔ Qualifications
- Skills are classified as: Knowledge, Skills (procedural/cognitive), and Attitudes/values
- IT-specific skills are in: "ICT skills" section + occupation-specific essential/optional skills
- Free API available: `https://esco.ec.europa.eu/en/use-esco/esco-api`

**Relevance to this thesis:**
ESCO is the most practical taxonomy for this project for four reasons:
1. It is multilingual — Armenian may be supported or adjacent via Russian, which is present
2. It was built specifically for education-employment linkage (not just job matching)
3. The API returns skill labels + descriptions + related occupations — directly usable for NLP matching
4. European relevance: Armenian universities are aligning with the Bologna Process (European framework), so ESCO is the appropriate taxonomy context

**How to use it in the thesis:**
- Use ESCO skill labels as the normalization target for extracted skills
- After extracting skill phrases from job descriptions and course names, match them to ESCO concepts via cosine similarity on ESCO skill descriptions
- This gives a "ESCO-normalized" skill profile for both curricula and jobs
- Gap analysis becomes: which ESCO skills appear in jobs but not curricula? Which appear in curricula but not jobs?

**Known limitation:** ESCO coverage of very recent skills (LLMs, specific frameworks) lags industry by 2–3 years. Skills like "prompt engineering" or "LangChain" will not be in ESCO. You will need a hybrid approach: ESCO-normalized skills + a residual set of domain-specific unmatched terms.

---

**Research use of ESCO — Chiarello, F., et al. (2021).** "Towards ESCO 4.0 – Is the European classification of skills in line with Industry 4.0?" *Technological Forecasting and Social Change*, 173. https://doi.org/10.1016/j.techfore.2021.121177

*What it does:* Applies text mining to check whether ESCO's current skill classification covers emerging Industry 4.0 skills (IoT, AI, robotics, etc.). Finds significant gaps.

*Lesson for this thesis:* If you use ESCO as your target taxonomy, expect some skill phrases from job postings (especially from cutting-edge companies like Picsart, Krisp, DataArt) to not match any ESCO concept. This is not a failure — it's a finding. Document the proportion of unmatched skills and report them separately as "emerging skills not captured in ESCO."

---

⚠️ **Musazade, N., et al. (2025).** "UniSkill: A Dataset for Matching University Curricula to Professional Competencies." *arXiv preprint 2603.03134*. https://arxiv.org/abs/2603.03134

*What it does:* Introduces a dataset linking university course descriptions to ESCO skills, specifically for Systems Analysts and Management Analyst occupations. Provides a benchmark for curriculum-to-ESCO matching.

*Lesson for this thesis:* This is the most directly parallel dataset to what this project is building. If the methodology holds up, it could be cited as a near-parallel study released around the same time as this thesis. **Note:** arXiv preprint — check if it was accepted to a venue before citing formally.

---

### 2.2 O*NET

**Source:** U.S. Department of Labor, https://www.onetcenter.org/

**What O*NET is:**
- U.S. occupational taxonomy: ~1,000 occupations with structured descriptors
- Dimensions: Skills, Knowledge, Abilities, Work Activities, Work Context, Interests, Work Values
- Freely available database (CSV download) + API
- Less relevant for Armenia specifically (US labor market framing) but useful as a secondary cross-reference

**Relevance to this thesis:**
O*NET is less appropriate than ESCO as the primary taxonomy because: (1) it is US-centric, (2) it uses different skill categories, (3) ESCO was designed specifically for the European education-employment interface that Armenia is approximating via Bologna.

*Recommended use:* Use O*NET as a secondary cross-validation source. If a skill cluster emerges that maps to an O*NET category, you can report both ESCO and O*NET labels to make the findings accessible to international readers from both EU and US academic contexts.

---

### 2.3 SFIA — Skills Framework for the Information Age

**Source:** https://sfia-online.org/

**What SFIA is:**
- IT-specific professional skills framework used in industry and academia
- 121 professional skills organized in 6 categories, 7 responsibility levels
- Widely used in university curriculum mapping for IT programs specifically
- Free to use, well-maintained

**Relevance to this thesis:**
SFIA is specifically designed for IT skills (as opposed to ESCO's broader scope). For a thesis focused on IT/CS programs, SFIA provides more granular IT skill categories than ESCO. However, it does not have an accessible public API or downloadable dataset, making it harder to use programmatically.

*Recommended use:* Use SFIA as a reference framework in the discussion chapter — when interpreting skill gaps, SFIA's 7-level responsibility structure (from level 1 "Follow" to level 7 "Set strategy") can help characterize *what kind* of skill gap exists (e.g., are universities producing level 2-3 graduates when the market needs level 4-5?).

---

### 2.4 Bloom's Taxonomy (for curriculum-side analysis)

**Anderson, L. W., & Krathwohl, D. R. (Eds.) (2001).** *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Educational Objectives.* Addison Wesley Longman.

*Original:* Bloom, B. S. (Ed.) (1956). *Taxonomy of Educational Objectives.* David McKay.

**What it is:**
A hierarchical model of cognitive learning: Remember → Understand → Apply → Analyze → Evaluate → Create.

**Relevance to this thesis:**
Course descriptions often contain Bloom-coded verbs (e.g., "students will *implement*...", "students will *analyze*..."). These can be used to:
1. Classify curriculum skills by cognitive depth, not just topic
2. Compare the cognitive level of what is taught vs. what jobs require
3. Show whether the gap is about *topics* (wrong skills) or *depth* (right skills taught at the wrong level)

*Practical note:* Bloom verb lists are freely available. You can add a lightweight Bloom classification step to the curriculum NLP pipeline using a lookup table of ~50 action verbs per level. This would add a methodologically interesting layer to the analysis at low cost.

---

## 3. Recommended Research Design for This Thesis

### 3.1 Overall Logic

This thesis is a **quantitative, data-driven comparative study** with an explanatory framing. The core claim being tested is: *there is a measurable gap between the skills encoded in Armenian IT university curricula and the skills demanded by the Armenian IT labor market*.

This is not a randomized experiment and not a survey study. It is a **corpus analysis** — both datasets (curricula and job postings) are treated as text corpora from which skills are extracted and then compared. The quantitative gap is the central finding; the university/program-level breakdown is the analytical layer; the sources of the gap (structural, economic, pedagogical) are interpreted qualitatively.

This design is consistent with Almaleh et al. (2019) as a precedent and appropriate for a master's thesis scope.

---

### 3.2 Research Design Options

**Option A: Extraction + Matching (Recommended for core analysis)**

Pipeline:
1. Extract skill phrases from job `full_text` → job skill inventory
2. Extract skill phrases from curriculum `course_name` + `description` → curriculum skill inventory
3. Normalize both inventories to ESCO concepts
4. Compute overlap, coverage, and gap metrics
5. Disaggregate by university, program, and degree level

*Strengths:* Reproducible, transparent, directly interpretable. Clean thesis argument.
*Weaknesses:* Quality depends on extraction precision. YSU Armenian text adds complexity.

---

**Option B: Embedding-Based Similarity (Recommended as secondary method)**

Instead of (or alongside) explicit skill extraction: represent each job posting and each course as a vector using a sentence transformer, then compute similarity scores.

*Why use this:* Handles synonymy and paraphrase naturally ("machine learning" ≈ "ML" ≈ "artificial intelligence"). Particularly useful for connecting vague course names (e.g., "Advanced Database Systems") to job requirements (e.g., "PostgreSQL", "query optimization").

*Recommended model:* `paraphrase-multilingual-mpnet-base-v2` (supports Armenian via multilingual training) or `all-MiniLM-L6-v2` (English only, faster).

*How to combine with Option A:* Use Option A for explicit skill extraction and gap reporting (interpretable, countable); use Option B as a validation step — if two skills are extractively different but semantically similar, the embedding method catches this and reduces false negatives.

---

**Option C: Predictive Modeling (Optional, low priority)**

Train a classifier to predict "will this job require skills taught in program X?" using historical alignment data. **Not recommended for this thesis** because:
- The dataset is a point-in-time snapshot (March 2026), not longitudinal
- 1,348 job postings is not large enough for a robust predictive model
- Adds complexity without a clear thesis argument payoff
- Better reserved for a follow-up paper or PhD work

*If supervisor asks for it:* Can be included as an exploratory section (logistic regression on extracted skill vectors), clearly labeled as preliminary.

---

**Option D: Mixed-Methods with Expert Validation (Optional enrichment)**

Run a brief online survey (Google Form, 10–15 minutes) with 5–10 IT professionals or hiring managers in Armenia, asking them to rate the importance of identified skill gaps and validate the top-10 gaps found computationally.

*When to include this:* If the thesis committee requires triangulation of quantitative findings, or if the quantitative results are ambiguous. Adds qualitative credibility.
*When to skip:* If timeline is tight. The computational results are self-standing.

---

### 3.3 Recommended Design for This Thesis

**Primary method:** Extraction + Matching (Option A) using KeyBERT or ESCO API
**Secondary method:** Embedding similarity (Option B) for validation and soft-skill coverage
**Optional add-on:** Bloom's taxonomy classification of curriculum side
**Skip:** Predictive modeling (Option C), survey (Option D) unless supervisor requests

**Justification:** This design matches the data actually available, is reproducible, and produces clear, communicable findings (gap tables, heatmaps, coverage percentages). It mirrors the most comparable published study (Almaleh et al. 2019) while extending it with a multi-source job dataset and a multi-university curriculum dataset in a new geographic context.

---

## 4. Proposed Analysis Pipeline

*Based on the actual data in this repository.*

```
CURRICULUM SIDE                              JOBS SIDE
final_curriculum_dataset.csv                final_jobs_dataset.csv
(1,161 rows, 18 cols)                       (1,348 rows, 13 cols)
        │                                          │
        ▼                                          ▼
[Step 1] TRANSLATION (YSU only)            [Step 3] SKILL EXTRACTION
  - 691 Armenian course names                - Apply KeyBERT to full_text
  - Helsinki-NLP/opus-mt-hy-en               - Extract top-K skill phrases per posting
    OR Google Translate API                  - Weight: company_portal rows weighted
  - Translate course_name + description        higher than aggregator rows (optional)
  - Store translated text alongside
    originals (preserve source_language)
        │                                          │
        ▼                                          ▼
[Step 2] SKILL EXTRACTION                  [Step 4] ESCO NORMALIZATION
  - Apply KeyBERT to:                        - Match extracted phrases → ESCO concepts
    • course_name (all 1,161 rows)             via cosine similarity on ESCO descriptions
    • description (940 rows: AUA + YSU)      - Threshold: similarity > 0.75 = match
    • course_name_original (for RAU          - Unmatched phrases: keep as "emerging skills"
      cross-validation)
  - Extract 3–7 skill phrases per course
        │                                          │
        ▼                                          ▼
[Step 5] NORMALIZATION (curriculum)        [Step 5] same
  - Match curriculum skill phrases           - Already done above
    → ESCO concepts
  - Build ESCO skill × course matrix
        │                                          │
        └──────────────┬──────────────────────────┘
                       ▼
            [Step 6] ALIGNMENT ANALYSIS
            - Jaccard overlap: curriculum skills ∩ job skills
            - Coverage rate: % of job skills present in curriculum
            - Gap set: job skills NOT in curriculum (skill demand gap)
            - Surplus set: curriculum skills NOT in job postings (curriculum surplus)
            - Disaggregate by: university, program, degree_level, source_type
                       │
                       ▼
            [Step 7] VISUALIZATION
            - Heatmap: program × top-50 ESCO skills (presence/absence)
            - Bar chart: top-20 demanded skills missing from curricula
            - Bubble chart: skill overlap by university
            - Table: per-program coverage score
```

---

### Step-by-step notes

**Step 1 — YSU translation**

The most uncertain step. Options:
- `Helsinki-NLP/opus-mt-hy-en` (HuggingFace): free, no API key, runs locally; quality varies for Armenian technical terms
- Google Cloud Translation API: better quality, costs ~$20 per 1M characters; 691 course names × ~20 chars = ~14,000 chars = negligible cost
- Manual review of translation output for technical terms is strongly recommended (sample 50 rows and check)

If translation quality is poor for specific technical terms, fall back to multilingual embeddings for those rows.

**Step 2 / Step 3 — Skill extraction with KeyBERT**

KeyBERT (Grootendorst, M., 2020; https://github.com/MaartenGr/KeyBERT) extracts keyword phrases using BERT embeddings. Practical usage:

```python
from keybert import KeyBERT
kw_model = KeyBERT(model="paraphrase-multilingual-mpnet-base-v2")
keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), top_n=7)
```

Strengths: out-of-the-box, works on short and long texts, multilingual model handles mixed-language content.
Weaknesses: extracts salience, not explicit skill mentions. Will pick up domain vocabulary but may miss implicit skills.

**Alternative:** Use the SkillSpan NER model (Zhang et al., 2022) for the English job postings side — this is a fine-tuned transformer specifically trained for skill span extraction from job ads. Better precision on skill phrases than KeyBERT for job ads. Would require installing from HuggingFace.

**Steps 4/5 — ESCO normalization**

ESCO API:
```
GET https://ec.europa.eu/esco/api/search?text=python programming&type=skill&language=en
```
Returns ranked ESCO skill matches with confidence scores. Alternatively, download the ESCO v1.2 skills CSV and do local embedding matching for speed.

Threshold decision: a similarity score of 0.75 is reasonable starting point. Run calibration on 50 manually labeled pairs to set the right threshold for your data.

**Step 6 — Gap metrics**

Key numbers to report:
- **Coverage rate** = |curriculum_skills ∩ job_skills| / |job_skills|, per university and overall
- **Gap count** = |job_skills \ curriculum_skills| (skills demanded but not taught)
- **Surplus count** = |curriculum_skills \ job_skills| (skills taught but not demanded)
- **Top-N gap skills** = highest-frequency job skills absent from curriculum

These should be computed at multiple granularities: all universities combined, per university, per program, bachelor vs master.

---

## 5. Tools and Resources Needed

### NLP / ML

| Tool | Purpose | Install |
|---|---|---|
| `keybert` | Skill keyword extraction | `pip install keybert` |
| `sentence-transformers` | Sentence embeddings for matching | `pip install sentence-transformers` |
| `spacy` | Tokenization, POS tagging, NER preprocessing | `pip install spacy` |
| `transformers` (HuggingFace) | Access to pre-trained models | `pip install transformers` |
| `torch` | Backend for transformer models | `pip install torch` |
| `Helsinki-NLP/opus-mt-hy-en` | Armenian → English translation model | via HuggingFace |

### Data and APIs

| Resource | Purpose | Access |
|---|---|---|
| ESCO API | Normalize extracted skills to EU taxonomy | Free, https://esco.ec.europa.eu/en/use-esco/esco-api |
| ESCO v1.2 CSV download | Local matching (faster than API at scale) | Free, https://esco.ec.europa.eu/en/use-esco/esco-data/download-esco |
| O*NET database | Secondary taxonomy cross-reference | Free CSV download, https://www.onetcenter.org/database.html |
| Google Translate API | YSU Armenian course name translation (if used) | ~$0.002 per 1K chars |

### Analysis and Visualization

| Tool | Purpose | Install |
|---|---|---|
| `pandas` | Data manipulation (already used) | already installed |
| `scikit-learn` | Cosine similarity, TF-IDF, optional clustering | `pip install scikit-learn` |
| `matplotlib` + `seaborn` | Heatmaps, bar charts, bubble charts | `pip install matplotlib seaborn` |
| `plotly` | Interactive charts (optional) | `pip install plotly` |

### Compute

- All models fit comfortably on a CPU for the dataset size (1,161 + 1,348 rows)
- `all-MiniLM-L6-v2` is fast enough on CPU (~1-2 seconds per batch of 32 texts)
- `paraphrase-multilingual-mpnet-base-v2` is slower but still feasible; use GPU if available
- Full pipeline (extract + normalize + analyze) estimated runtime: 15–30 minutes on CPU

---

## 6. Risks, Limitations, and Methodological Choices

### Risk 1: YSU Armenian language quality (HIGH IMPACT)

**Problem:** 691 of 1,161 curriculum rows have Armenian course names. Translation quality for Armenian technical terms is inconsistent — machine translation may garble domain-specific terms (e.g., "Ալգորիթմների տեսություն" = "Theory of Algorithms" may be OK; more specialized terms may not translate accurately).

**Mitigation:**
- Translate and manually sample 50–100 rows for quality
- For rows where translation confidence is low: use the multilingual embedding model directly on Armenian text rather than translation output
- Keep the original Armenian in `course_name_original` for verification
- Be transparent in the methodology section: "YSU courses were machine-translated; translation quality was validated on a sample of N rows"

---

### Risk 2: ESCO coverage gaps (MEDIUM IMPACT)

**Problem:** ESCO taxonomy lags industry by 2–3 years. Specific tools and frameworks (React, FastAPI, LangChain, etc.) will not appear in ESCO. Company portal job ads (Krisp, DataArt, Picsart) will contain many such terms.

**Mitigation:**
- Report ESCO-normalized skills and unmatched "emerging skills" separately
- The unmatched set is a finding in itself: these are the fastest-moving skill areas that formal taxonomies haven't yet captured
- Consider supplementing ESCO with a custom IT skills dictionary (manually curated from the top-50 most frequent unmatched terms)

---

### Risk 3: Small sample for company portals (LOW-MEDIUM IMPACT)

**Problem:** Company portal data totals only 281 rows across 8 companies. Picsart (2), DISQO (1), Synopsys (2) provide insufficient signal on their own. Aggregation is necessary.

**Mitigation:**
- Analyze company portals as a group, not individually
- Report EPAM (108) and SoftConstruct (152) separately as they have sufficient volume
- Clearly label results: "findings for company portal segment are based on N=281 postings from 8 companies active in Yerevan/Armenia as of March 2026"

---

### Risk 4: NPUA excluded (HIGH IMPACT ON REPRESENTATIVENESS)

**Problem:** The National Polytechnic University of Armenia (polytech.am) is blocked by Cloudflare and HTTP 403 for all automated access. NPUA has ~10 IT programs and ~11,000 students — potentially the largest technical university in Armenia. Its absence limits the representativeness of the curriculum side.

**Mitigation:**
- Acknowledge explicitly in limitations section
- Frame as a direction for future work
- Consider manual data entry from NPUA course catalogs if time permits (out of scope for this thesis)

---

### Risk 5: Skill extraction precision (MEDIUM IMPACT)

**Problem:** Skill extraction is inherently imprecise. KeyBERT extracts salient phrases but does not distinguish "skill" from "topic" or "context." A job description for a Python developer may heavily mention "REST API" (skill) and "microservices architecture" (concept) — both would be extracted but have different types of alignment implications.

**Mitigation:**
- Use SkillSpan (Zhang et al., 2022) for the English job postings side as a higher-precision alternative to KeyBERT
- Combine KeyBERT extraction with ESCO filtering: only keep phrases that match an ESCO skill concept (this acts as a relevance filter)
- Report confidence intervals or variance in gap estimates if feasible

---

### Risk 6: Time snapshot limitation (LOW IMPACT)

**Problem:** All data is from March 2026. The job market is dynamic; findings may not hold in 2027 or reflect pre-2026 conditions.

**Mitigation:** Frame explicitly as a cross-sectional study — a snapshot of the alignment state in early 2026. This is standard for this type of research and is acknowledged in all comparable studies (Almaleh et al., Aljohani et al.).

---

### Methodological Choice: Why not a survey?

A survey-based approach (asking graduates or employers about perceived skill gaps) would add face validity but is subject to recall bias, social desirability bias, and small sample constraints in Armenia's IT market. The computational approach used here is more reproducible, more scalable, and more transparent about what it measures. A hybrid approach (computational gap + expert validation of top-N gaps) is possible but adds timeline risk.

**Decision: computational approach only, with transparent limitations.** If a reviewer asks for validation: cite Kupets (2016) survey findings as external validation that a real gap exists in this context.

---

### Methodological Choice: Why ESCO over custom taxonomy?

Building a custom IT skill taxonomy from the ground up would require: (1) expert input, (2) ongoing maintenance, and (3) loss of comparability with other studies. Using ESCO allows results to be compared across countries and studies, and anchors the thesis in an established, well-documented standard. The limitation (ESCO coverage gaps) is a known and manageable problem.

---

## 7. Key Decisions Still Outstanding

These decisions should be made before beginning Phase 3:

| Decision | Options | Recommendation |
|---|---|---|
| YSU language handling | Translate first vs. multilingual embeddings | Translate first (Helsinki-NLP or Google), validate manually |
| Skill extraction method | KeyBERT vs. SkillSpan NER vs. ESCO API search | KeyBERT for both sides; SkillSpan for English job ads as validation |
| Target taxonomy | ESCO only vs. ESCO + custom supplement | ESCO primary, custom supplement for top unmatched terms |
| source_type weighting | Equal weight vs. company_portal weighted higher | Report both; weight discussion deferred to interpretation |
| Bloom classification | Include vs. skip | Include as lightweight add-on (lookup table, ~1 day of work) |
| Expert validation | Include survey vs. skip | Skip unless supervisor requires it |

---

## 8. Suggested Thesis Chapter Outline (Preliminary)

*For reference only — not a commitment to write in this order.*

| Chapter | Content | Key sources |
|---|---|---|
| 1. Introduction | Research question, motivation, Armenia context, thesis scope | Kupets 2016, WEF 2025 |
| 2. Literature Review | Skill gap research, curriculum alignment studies, NLP approaches | Almaleh 2019, Aljohani 2022, Zhang et al. 2022 |
| 3. Theoretical Framework | Constructive alignment, skill taxonomies, task-based view | Biggs & Tang 2011, Autor et al. 2003, ESCO, SFIA |
| 4. Data and Methodology | Dataset description, collection methods, NLP pipeline | This project's pipeline docs |
| 5. Results | Skill coverage, gap analysis, per-university findings | Data from analysis |
| 6. Discussion | Interpretation, comparison to related work, implications | Amirova & Valiyev 2021, Kupets 2016 |
| 7. Conclusion | Limitations, future work, policy recommendations | All sources |

---

*This document is a working research foundation, not a draft. Update as analysis decisions are made.*
*See also: `docs/scraping_methods_log.md` for technical methodology details.*
*See also: `docs/data_gaps_and_limitations.md` for dataset limitations.*
