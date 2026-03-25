# Chapter 4: Data and Methodology

## 4.1 Research Design

This thesis employs a quantitative, data-driven comparative study design. The central methodology is corpus analysis: two text corpora — one representing university curricula and one representing the labor market — are processed through a Natural Language Processing pipeline to extract skill profiles, which are then compared using alignment metrics. This design is cross-sectional: all data reflects a single point in time (March 2026) rather than a longitudinal trajectory.

The study follows a sequential multi-stage pipeline:

```
Stage 1: Data Collection     → curriculum scraping + job market scraping
Stage 2: Data Processing     → cleaning, normalization, unified schemas
Stage 3: Translation         → Armenian/Russian → English (YSU, RAU)
Stage 4: Skill Extraction    → TF-IDF and KeyBERT applied to both corpora
Stage 5: Normalization       → ESCO taxonomy matching
Stage 6: Alignment Analysis  → coverage rate, gap sets, surplus sets
```

This design is consistent with the methodological precedent established by Almaleh et al. [4], who applied a comparable two-corpus computational framework in the Saudi Arabian context. The present study extends that precedent by using a multi-source job dataset, a multilingual curriculum corpus, and a standardized EU skill taxonomy (ESCO) as the normalization target.

All data collection, processing, and analysis steps were implemented in Python (version 3.11) using Jupyter notebooks. The full pipeline is archived in the project repository alongside the datasets, enabling end-to-end reproducibility.

> **[Figure 4.1 — NLP Pipeline Overview]** *Insert pipeline flowchart here. See `docs/thesis/FIGURE_PLACEMENT_GUIDE.md` for specifications.*

---

## 4.2 Curriculum Dataset

### 4.2.1 Sources and Collection Strategy

Curriculum data was collected from four Armenian universities whose IT-related programs were publicly accessible in structured or semi-structured form at the time of collection (February–March 2026). The selection of universities was determined by data accessibility, not by random or stratified sampling — a limitation discussed in Section 4.7.

**Table 4.1 — Curriculum data sources**

| University | Abbr. | Programs | Courses | Source format | Language |
|---|---|---|---|---|---|
| Yerevan State University | YSU | 13 | 691 | Web scrape (Apify, markdown) | Armenian |
| American University of Armenia | AUA | 7 | 249 | Web scrape (Apify, HTML catalog) | English |
| National University of Architecture and Construction of Armenia | NUACA | 4 | 174 | Web scrape (Apify, plain text) | English |
| Russian-Armenian University | RAU | 1 | 47 | PDF study plans (PyPDF2 + regex) | Russian |
| **Total** | | **25** | **1,161** | | |

Each university required a distinct collection approach due to differences in how curriculum data was published online.

**YSU** curriculum data was collected using the Apify cloud scraping platform, which rendered JavaScript-heavy pages into structured markdown. YSU publishes program pages listing courses for each academic year across multiple faculties. A total of 19 program pages were scraped across five faculties; six non-IT programs (Finance, Management, and Economics at Bachelor and Master levels) were subsequently excluded based on the IT-scope filter defined in Section 4.7.1. Three program URLs returned HTTP 404 and are treated as inactive. The final YSU contribution is 691 courses across 13 programs, covering both Bachelor and Master levels.

**AUA** curriculum data was collected from the Computer Science and Engineering department's public course catalog at `cse.aua.am/courses/`, which provides a structured listing of all courses including full English descriptions, prerequisite requirements, and credit values. AUA's catalog is the richest source in the dataset in terms of per-course metadata: 242 of 249 courses carry full text descriptions averaging several hundred words each.

**NUACA** curriculum data was collected from Faculty of Management and Technology program pages. The source format is plain-text course listings without descriptions. All five IT-related programs are included; additional non-IT programs (Economics, Accounting, Logistics) were identified but excluded as out of scope.

**RAU** curriculum data was extracted from official PDF study plans (учебные планы) downloaded from `impht.rau.am` and `rau.am/sveden/education/eduop`. The PDFs follow a standardized Russian federal format (tabular layout with course codes, names, credit values, and assessment types) and were parsed using PyPDF2 with regular expression extraction. Course names were translated from Russian to English during the parsing step. Coverage at RAU is limited to one bachelor-level program (Applied Mathematics and Informatics, code 01.03.02); additional programs were identified but not parsed within the scope of this project.

### 4.2.2 Data Processing and Schema

All four source-specific datasets were merged into a single unified analysis file: `data/processed/university/final_curriculum_dataset.csv`. Prior to merging, the following cleaning and harmonization steps were applied:

- **YSU deduplication:** 129 exact within-program duplicate rows were removed (artifacts of the Apify scraping process which occasionally re-scraped the same course block). Uniqueness was defined as exact match on (program\_name, course\_name, academic\_year).
- **NUACA normalization:** Assessment values were standardized ("Exam." → "Exam"; "Test." → "Test").
- **YSU program name correction:** The Apify scraper captured official Armenian speciality codes (e.g., "056201 — Statistics") rather than actual program titles. These were corrected via URL-based mapping against the manually verified reference dataset, resulting in meaningful program names such as "Applied Statistics and Data Science" and "Data Science in Business."
- **Credit system differences:** Credit systems differ across universities (YSU and NUACA use ECTS-compatible hours; AUA uses US credit hours; RAU uses Russian зачётные единицы). Credits were retained in their original units in the `credits` column and are not used as normalized weights in the analysis.

**Table 4.2 — Unified curriculum dataset schema (selected columns)**

| Column | Type | Coverage | Description |
|---|---|---|---|
| `course_id` | int | 100% | Sequential row identifier |
| `university` | string | 100% | Full university name |
| `program_name` | string | 100% | English program name |
| `degree_level` | string | 100% | Bachelor / Master / General |
| `course_name` | string | 100% | Original-language course title |
| `course_name_en` | string | 100% | English course title (translated for YSU/RAU) |
| `description` | string | 81%* | Original-language course description |
| `description_en` | string | 81%* | English course description (translated for YSU) |
| `credits` | float | 74% | Credit value in source system |
| `source_language` | string | 100% | Armenian / English / Russian |

*Description coverage: AUA 242/249 (97%), YSU 691/691 (100%), NUACA 0/174 (0%), RAU 0/47 (0%).

The final dataset contains **1,161 rows** across **27 program–degree combinations** at **4 universities**, covering Bachelor, Master, and General Education coursework.

---

## 4.3 Job Market Dataset

### 4.3.1 Sources and Collection Strategy

Job market data was aggregated from a 14-source market snapshot representing the Armenian IT labor market as of March 2026. Sources were selected to maximize coverage of employer types and seniority levels within the Armenian market, combining broad aggregators that index many employers with direct company career portals that represent the largest IT employers in Yerevan. A later filtering step derives the IT-only analysis subset used in downstream NLP and alignment stages.

**Table 4.3 — Job market data sources**

| Source | Type | Method | Postings |
|---|---|---|---|
| LinkedIn | Aggregator | Apify LinkedIn Jobs scraper | 992 |
| SoftConstruct | Company portal | Requests + BeautifulSoup (PeopleForce ATS) | 152 |
| EPAM Armenia | Company portal | Internal careers API (JSON) | 108 |
| Staff.am | Aggregator | Next.js `__NEXT_DATA__` JSON + JSON-LD | 55 |
| job.am | Aggregator | Requests + BeautifulSoup (SSR HTML) | 20 |
| Grid Dynamics | Company portal | Requests + API-backed listing extraction | 11 |
| Krisp | Company portal | Requests + BeautifulSoup (SSR HTML) | 7 |
| NVIDIA | Company portal | Requests + SSR/API extraction | 5 |
| 10Web | Company portal | Requests + SSR/API extraction | 5 |
| DataArt | Company portal | `window.INITIAL_STATE` (React SPA) + Playwright | 5 |
| ServiceTitan | Company portal | Workday listing API + Playwright detail | 4 |
| Picsart | Company portal | Greenhouse public API (Armenia filter) | 2 |
| Synopsys | Company portal | Avature ATS SSR HTML + JSON-LD | 2 |
| DISQO | Company portal | Lever public API | 1 |
| **Total (broad snapshot)** | | | **1,369** |

Collection for each source was implemented in a dedicated Jupyter notebook (notebooks 01–11 in `notebooks/1_collection_jobs/`). All scrapers used Python's `requests` library and `BeautifulSoup` for server-rendered HTML sources; Playwright headless browser automation was used for JavaScript-heavy sources (DataArt, ServiceTitan) where the listing metadata or job content was not accessible via static requests. Each scraper included rate limiting (minimum 1.5-second delay between requests) and a custom User-Agent identifying the purpose as academic research. All sources were confirmed compliant with their respective `robots.txt` policies at the time of collection.

The choice to include both aggregators and company portals was deliberate. Aggregators (LinkedIn, Staff.am, job.am) provide broad market coverage but may contain duplicates, outdated postings, and variable description quality. Company portals represent direct employer demand — the job descriptions are written by the hiring company with no intermediary — and typically contain higher-quality skill specifications. The `source_type` column encodes this distinction, enabling separate analysis of the two segments.

### 4.3.2 Data Processing and Schema

Across 14 sources, raw data varied significantly in structure (HTML tables, JSON-LD Schema.org blocks, proprietary API responses, Next.js embedded state). A canonical schema was defined prior to collection, and each source-specific standardization notebook applied a `to_canonical()` transformation to normalize raw fields into the shared schema.

**Table 4.4 — Canonical job dataset schema**

| Column | Coverage | Description |
|---|---|---|
| `source` | 100% | Source identifier (e.g., "linkedin", "epam") |
| `source_type` | 100% | "aggregator" or "company\_portal" |
| `source_url` | 100% | Direct URL of the job posting |
| `job_title` | 100% | Job title as posted |
| `company_name` | 100% | Hiring company name |
| `location` | 100% | City/country |
| `employment_type` | 100% | Full-time / Part-time / Contract |
| `seniority_level` | 100% | Junior / Mid / Senior / Lead / C-level |
| `industries` | 100% | Industry tags |
| `posting_date` | 87% | ISO date of original posting |
| `skills_tags` | 100% | Structured skill tags where available |
| `full_text` | 100% | Full job description text (key NLP input) |

The `full_text` field — the primary input for skill extraction — achieves 100% coverage across all rows. It was constructed as the concatenation of description, responsibilities, and required qualifications fields where these were separate in the source, or as the full description text where they were unified.

### 4.3.3 Broad Snapshot and IT-Only Filtering

The broad market snapshot used in the current project contains **1,369 postings** merged into a shared 13-column schema. This broad snapshot is preserved as `final_jobs_dataset.csv` for transparency and reproducibility.

Because the broad Armenia tech hiring landscape still includes clearly non-technical, managerial, commercial, and mixed-role postings, a dedicated IT-only filtering step was introduced before downstream NLP analysis. The filter combines job-title rules, lexical technical cues, and manual review flags. The resulting analysis subset contains **753 IT-only postings**. The full audit is stored in `it_job_filter_audit.csv` (`keep=753`, `drop=558`, `review=58`), and ambiguous cases are preserved in `it_job_filter_review_queue.csv`.

This separation between the broad market snapshot and the IT-only downstream subset is methodologically important. It preserves the full market collection for descriptive reporting while preventing obviously non-IT roles from distorting the skill-demand signal used for alignment analysis.

---

## 4.4 Multilingual Data Handling and Translation

### 4.4.1 The Multilingual Challenge

The curriculum dataset contains text in three languages: Armenian (YSU, 691 rows), English (AUA and NUACA, 423 rows), and Russian (RAU, 47 rows). The job market dataset is predominantly in English, with some Armenian-language postings from local aggregators (Staff.am, job.am). For skill extraction to operate on a common vocabulary, all curriculum text must be available in English prior to the NLP phase.

Two strategies were evaluated:

- **Option A (Translation-first):** Machine-translate all non-English curriculum text to English, then apply English-language skill extraction uniformly.
- **Option B (Multilingual embeddings):** Apply a multilingual sentence transformer (`paraphrase-multilingual-mpnet-base-v2`) directly to the original Armenian/Russian text, relying on cross-lingual embedding alignment to bridge the language gap.

Option A was selected as the primary approach because it produces interpretable, human-readable translated text that can be manually validated, reported in the thesis, and verified by reviewers who do not read Armenian. Option B was retained as a secondary validation method (see Section 4.6).

### 4.4.2 Translation Pipeline

Armenian-language course names and descriptions (691 rows, both `course_name` and `description` fields) were translated to English using the OpenAI API (`gpt-4o-mini` model). The translation was prompted with a task-specific system instruction that specified:

- Preserve technical terms already in English (programming languages, framework names, algorithm names)
- Keep English terms embedded in Armenian text (a common pattern in YSU course names where English terms appear in parentheses, e.g., "Մեծ տվյալների տեխնոլոգիաներ" has a standalone Armenian title, while "Համակարգչային տեսողություն (Computer Vision)" already contains the English equivalent)
- Produce clean academic English — no explanations, summaries, or added content
- Output only the translated text

Prior to the full run, two translation providers were compared on a stratified 50-row sample drawn across all 13 YSU programs: OpenAI `gpt-4o-mini` and Perplexity Sonar Pro (accessed via OpenAI-compatible API). OpenAI substantially outperformed Perplexity on this task: while OpenAI consistently produced accurate, concise translations, Perplexity Sonar — a search-augmented language model — treated course name inputs as search queries and returned search result summaries rather than translations. In one illustrative failure case, the Armenian word "Փայթն" (Python, written phonetically in Armenian script) was translated by Perplexity as "Explosion" (a false cognate of the Armenian word), while OpenAI correctly rendered it as "Python." On the 50-row sample, OpenAI scored 20/20 across four quality criteria (technical accuracy, academic naturalness, English term preservation, description completeness); Perplexity scored 6/20. All subsequent translation was performed with OpenAI.

**Table 4.5 — Provider comparison on 50-row translation sample**

| Criterion | OpenAI gpt-4o-mini | Perplexity Sonar Pro |
|---|---|---|
| Technical term accuracy | 5/5 | 2/5 |
| Academic English naturalness | 5/5 | 1/5 |
| English terms in parentheses preserved | 5/5 | 2/5 |
| Description completeness (no hallucination) | 5/5 | 1/5 |
| **Total** | **20/20** | **6/20** |

The full translation run processed 691 rows × 2 fields = 1,382 translation calls. All translations are cached in `data/processed/university/translation_cache.json`, keyed by MD5 hash of the provider and input text, ensuring that re-running the pipeline does not incur additional API costs. Russian course names at RAU had already been translated to English during the PDF parsing step (Section 4.2.1) and did not require re-translation.

The translated output is stored in `data/processed/university/ysu_translated.csv`, which extends the unified curriculum dataset with two additional columns: `course_name_en` (English course title for all 1,161 rows) and `description_en` (English description for all rows where descriptions are available). For non-Armenian rows, `course_name_en` is set equal to `course_name` (passthrough).

A manual spot-check of 50 randomly selected translated course names confirmed accurate rendering of domain-specific terminology including neural network architectures, database systems, statistical methods, and programming paradigms. Two minor terminology errors were identified: "Ալիքային" (wave) was rendered as "digital" in one instance, and "Տվյալների հենքերի կառավարում" was translated as "Data Structures Management" rather than the more precise "Database Management." Both errors are within the tolerance of the downstream ESCO normalization step, which will match based on semantic similarity rather than exact string matching. The original Armenian text is preserved in the `course_name` and `description` columns of the dataset for reference and verification.

---

## 4.5 Skill Extraction Pipeline

### 4.5.1 Approach Selection

Skill extraction — identifying skill-denoting phrases in free text — is the methodologically critical step in this pipeline. Two unsupervised approaches were implemented and compared as baselines before ESCO normalization:

**TF-IDF keyword extraction** uses term frequency–inverse document frequency weighting [22] (sklearn `TfidfVectorizer` [19]) to identify terms that are distinctive to a given document relative to the corpus. It operates at corpus scale, treating the entire curriculum or job market corpus as the reference distribution, and selects n-grams whose TF-IDF weight ranks highest for each individual document. For a term $t$ in document $d$ drawn from corpus $D$, the TF-IDF weight is:

$$\text{TF-IDF}(t, d, D) = \frac{f_{t,d}}{\displaystyle\sum_{t' \in d} f_{t',d}} \cdot \log\frac{|D| + 1}{1 + |\{d' \in D : t \in d'\}|}$$

where $f_{t,d}$ is the raw count of term $t$ in document $d$. This method captures terminology that is specific to individual courses or postings rather than terminology common across the corpus.

**KeyBERT** [9] uses a sentence transformer to represent the full document as an embedding, then ranks candidate n-grams by their cosine similarity to the document embedding — identifying the phrases that best represent the semantic content of the text. For candidate phrase $p$ and document $d$, cosine similarity is:

$$\text{sim}(p, d) = \frac{\mathbf{e}_p \cdot \mathbf{e}_d}{\|\mathbf{e}_p\| \cdot \|\mathbf{e}_d\|}$$

where $\mathbf{e}_p$ and $\mathbf{e}_d$ are the phrase and document embeddings produced by the sentence transformer. This approach handles short texts well (a course name of five words is sufficient) and requires no domain-specific training data.

Both methods were applied to all 1,161 curriculum documents and the 753-posting IT-only job subset, enabling comparison of their alignment metrics prior to ESCO normalization.

The sentence transformer model for KeyBERT is `all-MiniLM-L6-v2` [12], a lightweight English model (22M parameters) whose architecture builds on Sentence-BERT [11]. This model was selected over the larger multilingual alternative (`paraphrase-multilingual-mpnet-base-v2`, 278M parameters) for two reasons: (1) all curriculum text is available in English after the translation step described in Section 4.4, making a multilingual model unnecessary; (2) the smaller model allows the full extraction pipeline to run on a standard laptop without hardware accelerators, within the practical constraints of this project.

### 4.5.2 Text Preprocessing for Skill Extraction

Prior to extraction, both corpora underwent preprocessing steps designed to remove non-skill content that would otherwise dominate the extracted keyword sets:

**Input text construction.** For curriculum documents, the input text was constructed by concatenating the English course name (`course_name_en`) and English description (`description_en`), separated by a period. For job postings, the `full_text` field (concatenated description, responsibilities, and requirements) was used directly. This ensures that short course names receive contextual enrichment from their descriptions where available.

**Boilerplate removal.** Job descriptions often contain standardized paragraphs — company "About Us" blurbs, equal employment opportunity statements, and ATS submission instructions — that appear verbatim across multiple postings. Such paragraphs, if left in, cause KeyBERT to extract company identity phrases ("Xometry NASDAQ XMTR") rather than skills. A paragraph was classified as boilerplate if it appeared identically (after whitespace normalization) in four or more job postings across the corpus. This threshold identified 140 boilerplate paragraphs, which were removed from all job posting texts before extraction.

**Expanded stopword list.** Sklearn's built-in English stopword list was supplemented with approximately 295 domain-specific stopwords plus 459 generic English unigrams, organized in several categories:

- *Academic filler:* verbs and nouns that appear frequently in course descriptions but do not denote skills, including procedural verbs ("familiarize", "introduce", "examine"), pedagogical terms ("lecture", "instructor", "semester"), and evaluation language ("exam", "grade", "credit").
- *Job posting filler:* boilerplate language common in job postings but not indicative of skills, including hiring language ("seeking", "candidate", "apply"), vague qualifiers ("proven", "strong", "excellent"), and generic nouns ("opportunity", "benefit", "environment").

**Company name token filtering.** Tokens extracted from the `company_name` field of the jobs dataset were compiled into a blocklist. Any extracted keyword whose constituent tokens were all company name tokens was rejected (with an exception for tokens that are also legitimate skill words, such as "data", "cloud", or "mobile").

**Skill-likeness post-filter.** A final filter (`is_skill_like()`) was applied to all extracted phrases, rejecting: pure numeric strings, single-word generics from a curated list of 459 terms, known noise phrases (e.g., "cutting edge", "wide range"), multi-word phrases where more than 60% of tokens are stopwords, and phrases shorter than three characters.

### 4.5.3 Extraction Configuration

**TF-IDF** configuration:
```python
TfidfVectorizer(
    ngram_range=(1, 3),       # unigrams, bigrams, trigrams
    max_df=0.85,              # ignore terms in >85% of docs
    min_df=2,                 # ignore terms in <2 docs
    stop_words=combined_stops,  # sklearn defaults + custom domain stops
    max_features=15000
)
```

**KeyBERT** configuration:
```python
kw_model = KeyBERT(model='all-MiniLM-L6-v2')
keywords = kw_model.extract_keywords(
    text,
    keyphrase_ngram_range=(1, 3),
    stop_words='english',
    use_mmr=True,    # Maximal Marginal Relevance for diversity (O(n·k), vs MaxSum O(n²))
    diversity=0.5,
    top_n=15         # extract extra; post-filter to 10
)
```

Up to 10 skill phrases per document are retained after post-filtering. The `use_mmr=True` parameter applies Maximal Marginal Relevance (MMR) [17] to select diverse top phrases, reducing extraction of near-duplicate variants of the same concept. At each step, MMR selects the candidate phrase $c_i$ from the remaining set $C \setminus S$ that maximizes:

$$\text{MMR} = \underset{c_i \in C \setminus S}{\arg\max}\left[\lambda \cdot \text{sim}(c_i,\, d) - (1 - \lambda) \cdot \underset{c_j \in S}{\max}\, \text{sim}(c_i,\, c_j)\right]$$

where $S$ is the set of already-selected phrases, $d$ is the document embedding, and $\lambda = 0.5$ balances relevance to the document against redundancy with already-selected phrases. MMR was preferred over the Max-Sum algorithm (`use_maxsum=True`) for computational efficiency: MMR runs in $O(n \cdot k)$ time per document while MaxSum requires $O(n^2)$ pairwise comparisons, making MaxSum impractical at corpus scale on a CPU-only machine.

For course names (typically 3–8 words), the combined course name + description provides sufficient context. For job postings (median ~3,200 characters), the full `full_text` after boilerplate removal is used.

### 4.5.4 ESCO Normalization

Raw extracted phrases ("machine learning algorithms", "neural network training", "deep learning frameworks") refer to the same conceptual domain but use different surface forms. ESCO normalization maps these to a shared vocabulary of 13,939 standardized skill concepts, enabling direct comparison between curriculum-derived and job-derived skill profiles.

Normalization is performed via cosine similarity matching. The ESCO v1.2 skills dataset [14] — downloaded as a CSV file for local matching — provides a preferred label and description for each skill concept. Each extracted phrase and each ESCO skill label are encoded using the `all-MiniLM-L6-v2` sentence transformer [12], and the extracted phrase $p$ is mapped to the ESCO concept $e^*$ with the highest cosine similarity above threshold $\tau = 0.75$:

$$e^*(p) = \underset{e \in \mathcal{E}}{\arg\max}\; \text{sim}(p, e) \qquad \text{subject to}\quad \text{sim}(p, e^*) \geq \tau$$

Phrases that do not match any ESCO concept above the threshold are retained as an "emerging skills" set rather than discarded. These unmatched phrases — representing recent technical terminology not yet absorbed by the ESCO taxonomy (e.g., specific cloud service APIs, LLM-related tooling) — are reported separately as a finding in Chapter 5, following the recommendation of Chiarello et al. [15] who document ESCO's lag in coverage of Industry 4.0 skills.

The threshold $\tau = 0.75$ was selected through the calibration procedure described in Section 4.5.6 and then used in the completed ESCO normalization stage.

### 4.5.5 Baseline Results (Pre-ESCO)

Before ESCO normalization, alignment was measured directly on the raw extracted skill sets as a baseline. These baseline metrics (Table 4.6) are expected to underestimate true alignment, since semantically equivalent phrases with different surface forms (e.g., "machine learning" vs. "ml") are counted as separate non-overlapping skills. They serve as a lower bound on alignment and as a method comparison between TF-IDF and KeyBERT.

**Table 4.6 — Baseline alignment metrics (raw extracted skills, before ESCO normalization)**

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Curriculum unique skills | 3,442 | 4,812 |
| Job unique skills | 3,153 | 5,530 |
| Overlap | 279 | 18 |
| Coverage rate | 8.85% | 0.33% |
| Jaccard similarity | 4.42% | 0.17% |
| Gap (jobs only) | 2,874 | 5,512 |
| Surplus (curriculum only) | 3,163 | 4,794 |

The difference between TF-IDF (8.85%) and KeyBERT (0.33%) at the raw phrase level is expected and does not indicate a quality problem. TF-IDF extracts corpus-specific vocabulary, producing overlapping terms like "algorithms", "analytics", "python", "sql", and "cloud" — words that appear across both corpora using identical surface forms. KeyBERT extracts semantically rich keyphrases that are idiomatic to each text (e.g., "object oriented programming" in curriculum vs. "backend development" in jobs), which rarely match verbatim. After ESCO normalization maps both sets to shared concept identifiers, the alignment numbers for KeyBERT rise substantially. The TF-IDF coverage of 8.85% provides a literal string-match lower bound; the post-ESCO result in Chapter 5 provides the primary finding.

Note: an earlier version of this pipeline reported a TF-IDF overlap of 12.6% (584 terms). A systematic audit revealed that approximately 60% of those overlap terms were generic English words (e.g., "access", "achieve", "activities") rather than skills. After expanding the generic word filters from ~130 to 459 terms, tightening the multi-word noise filter, and restricting the demand-side corpus to the IT-only subset, the overlap settled at the more accurate 279 terms (8.85%). Validation against 151 jobs with human-curated `skills_tags` from Staff.am and EPAM yielded a soft-match recall of 44.2% for TF-IDF and 20.5% for KeyBERT, confirming that the pipeline captures a reasonable share of ground-truth skills despite operating unsupervised.

Note: a visual inspection of both output files confirms that the extraction quality is qualitatively reasonable — TF-IDF curriculum top terms include `data`, `programming`, `algorithms`, `mathematics`, `machine` (learning), `analysis`, `statistics`; TF-IDF jobs top terms include `data`, `testing`, `cloud`, `backend`, `automation`, `security`, `software`. The gap between them (low raw overlap despite conceptual similarity) illustrates exactly the vocabulary fragmentation problem that ESCO normalization is designed to solve.

### 4.5.6 ESCO Threshold Calibration

To validate the cosine similarity threshold empirically rather than adopting a value from prior work without verification, a calibration sample was constructed from extracted skills. Two hundred and ninety-three phrase–ESCO pairs were drawn from the TF-IDF and KeyBERT extraction outputs, stratified across seven cosine similarity bands (below 0.60 through above 0.85), to cover the full range of match quality.

**Annotation procedure.** Given the volume of pairs and the well-defined binary nature of the judgment task, annotation was performed using GPT-4o-mini as an automated judge [18], following the LLM-as-annotator approach established in recent NLP research [20, 21]. Each pair was submitted individually with a structured system prompt requiring a binary output: 1 (the extracted phrase and ESCO label refer to the same competency) or 0 (surface similarity without conceptual alignment). The model was run at temperature=0 to ensure deterministic, reproducible outputs.

To validate the automated annotations, a stratified sample of 35 pairs (5 per similarity band) was reviewed manually by the author. Inter-annotator agreement between GPT-4o-mini and the human reviewer was 94.3% (33/35 pairs). Two corrections were applied: a phrase describing ERP–ecommerce integration incorrectly matched to "e-commerce systems", and "chemical data analysis" incorrectly matched to "analyse chemical substances" (a laboratory skill). Corrected pairs are flagged in the dataset with `annotator_notes = "gpt-4o-mini; corrected by human reviewer"`.

Precision, recall, and F1 were computed at thresholds 0.60, 0.65, 0.70, 0.75, 0.80, and 0.85. The threshold yielding the highest F1 score was selected as the operating point. Results are reported in Section 5.1 alongside the main skill normalization findings.

> **[Figure 4.3 — ESCO Threshold Calibration Curve]** *Insert precision/recall/F1 vs. threshold line chart here. Export from `notebooks/3_analysis/04_esco_calibration.ipynb`.*

The calibration procedure is implemented across `notebooks/3_analysis/04_esco_calibration.ipynb` (pair generation and threshold sweep) and `notebooks/3_analysis/04b_annotate_calibration_pairs.ipynb` (annotation and manual validation).

### 4.5.7 Sensitivity Analysis

Three sensitivity analyses were conducted to assess the robustness and quality of the extraction pipeline before proceeding to ESCO normalization. Full details and code are in `notebooks/3_analysis/03_sensitivity_analysis.ipynb`.

#### 4.5.7.1 Description Asymmetry

A significant source of measurement asymmetry in the curriculum corpus is the uneven availability of course descriptions across universities. Two universities (NUACA with 174 courses and RAU with 47 courses) contribute no descriptions to the dataset — skill extraction for these 221 courses relies solely on the course name, typically 3–8 words. By contrast, AUA (242 courses) contributes descriptions averaging approximately 200 words per course, and YSU (691 courses) contributes descriptions translated from Armenian averaging 80 words per course.

To quantify this effect, AUA was used as a controlled test case: skill extraction was run twice on AUA courses — once using only course names, and once using names combined with descriptions. Table 4.7 presents the results.

**Table 4.7 — AUA sensitivity test: impact of course descriptions on skill extraction**

| Metric | Names Only | Names + Descriptions |
|---|---|---|
| Courses processed | 235 | 248 |
| Avg skills per course | 1.8 | 9.6 |
| Unique curriculum skills | 124 | 1,277 |
| Overlap with job market | 61 | 315 |
| Coverage rate | 1.3% | 6.8% |

The results demonstrate a 5x multiplier on coverage when descriptions are available. Course names alone (3–8 words) provide insufficient text for meaningful TF-IDF extraction — the vectorizer produces only 1.8 skills per course on average, compared to 9.6 with descriptions.

> **[Figure 4.2 — University Description Coverage]** *Insert stacked bar chart of description availability by university (AUA 97%, YSU 100%, NUACA 0%, RAU 0%). Create from Table 4.2 data.*

This finding has two implications for interpreting the results in Chapter 5:

1. **NUACA and RAU alignment scores are lower bounds.** Their true skill coverage is likely 3–5x higher than reported, but cannot be measured without course descriptions.
2. **Cross-university comparisons are valid only within description-availability groups:** AUA and YSU (with descriptions) can be compared to each other; NUACA and RAU (without descriptions) form a separate group. Comparing across groups conflates data quality differences with genuine curriculum differences.

#### 4.5.7.2 Validation Against Human-Curated Skill Tags

A subset of 151 job postings (104 from EPAM, 47 from Staff.am) contain structured `skills_tags` fields — human-curated skill labels assigned by recruiters or platform algorithms. These tags serve as approximate ground truth for evaluating extraction quality. The validation compared NLP-extracted skills against these tags using two match criteria:

- **Exact match:** the extracted skill string appears verbatim in the tag set
- **Soft match:** either the extracted skill contains a tag as a substring, or vice versa (e.g., extracted "python programming" matches tag "python")

**Table 4.8 — Validation of NLP extraction against human-curated skills_tags (151 jobs)**

| Metric | TF-IDF | KeyBERT |
|---|---|---|
| Exact match recall | 14.5% | 0.1% |
| Soft match recall | 44.2% | 20.5% |
| Precision proxy | 20.3% | 10.7% |
| F1-like (soft match) | 27.9% | 14.1% |

When soft skills intentionally excluded by the pipeline (teamwork, problem solving, time management, etc.) are removed from the tag set, technical-only recall rises to 45.7% for TF-IDF and 21.5% for KeyBERT.

The recall ceiling is explained by three factors: (1) soft skills are intentionally filtered by the stopword list — this is correct behavior for IT skill extraction; (2) special-character tokens (`C#`, `.NET`, `Node.js`) are mangled by the TF-IDF tokenizer's regex pattern; and (3) TF-IDF's `min_df=2` parameter drops terms appearing in only one document, which eliminates niche technologies from small-corpus extraction. These are known limitations documented in Section 4.8.

The precision proxy of 20.3% is a lower bound — it counts an extracted skill as "incorrect" if it does not appear in the tag set, even when the skill is a legitimate extraction from the job description text. The tag sets are sparse (averaging 5.1 tags per job) while the pipeline extracts up to 10 skills, so many valid extractions have no corresponding tag.

#### 4.5.7.3 Noise Audit and Filter Expansion

A systematic audit of the initial TF-IDF overlap set (584 terms at 12.6% coverage) revealed that approximately 60% of overlapping terms were generic English words appearing in both corpora without being IT skills — words such as "access", "achieve", "activities", "challenges", "comprehensive", "effective", "innovation", and "transformation".

The generic unigram filter was expanded from approximately 130 terms to 459 terms, and 11 multi-word noise phrases were added (e.g., "cutting edge", "wide range", "data data"). The multi-word filter threshold was tightened from 70% to 60% stop-word ratio. After re-running extraction with the expanded filters and then restricting the demand-side corpus to the IT-only subset, the TF-IDF overlap fell from 584 terms (12.6% coverage) to 279 terms (8.85% coverage). The remaining overlap terms are predominantly genuine IT skills: `algorithms`, `analytics`, `angular`, `automation`, `blockchain`, `cloud`, `cybersecurity`, `data science`, `database`, `deployment`, `javascript`, `python`, `sql`, `testing`, `visualization`.

KeyBERT overlap was unaffected by the noise cleanup (23 terms before and after), confirming that KeyBERT's semantic extraction already produces domain-specific phrases that do not suffer from the generic-word problem inherent to frequency-based methods.

---

## 4.6 Alignment Metrics

Following skill extraction and ESCO normalization, the curriculum and job market skill profiles are compared using four metrics:

Let $C$ denote the set of ESCO skill concepts present in the curriculum corpus and $J$ the set present in the job market corpus. Four metrics are computed:

**Coverage rate** measures what proportion of employer-demanded skills are represented in the curriculum:

$$\text{CR}(C, J) = \frac{|C \cap J|}{|J|}$$

A coverage rate of 1.0 would mean every skill demanded in job postings is also taught in the curriculum; 0.25 means one in four demanded skills is covered.

**Gap set** is the set of skills demanded by employers but absent from the curriculum:

$$\text{gap}(C, J) = J \setminus C = \{s \in J : s \notin C\}$$

Gap skills are ranked by their frequency of occurrence in job postings to prioritize the most actionable curriculum interventions.

**Surplus set** is the set of skills present in the curriculum but not found in any job posting:

$$\text{surplus}(C, J) = C \setminus J = \{s \in C : s \notin J\}$$

A large surplus does not necessarily indicate poor curriculum quality — foundational theoretical content may not appear explicitly in job descriptions while still underpinning applied competences — but it is reported as a finding for discussion.

**Jaccard similarity** provides a symmetric, size-normalized overlap score:

$$\text{Jaccard}(C, J) = \frac{|C \cap J|}{|C \cup J|}$$

All four metrics are computed at four levels of granularity: (1) overall (all universities combined vs. all job postings), (2) per university, (3) per program, and (4) Bachelor vs. Master degree level. Company portal and aggregator job postings are analyzed separately to assess whether the two source types exhibit different skill demand profiles.

---

## 4.7 Ethical Considerations and Data Governance

All data collected in this study was sourced from publicly accessible web pages and APIs. No personal data, private communications, or user-generated content behind authentication was collected. Job postings are public documents published by employers for the purpose of attracting applicants; their use for academic research is consistent with their intended public function.

Web scraping was conducted in compliance with the `robots.txt` policies of all source websites at the time of collection. All scrapers implemented rate limiting (minimum 1.5-second delay between requests) and identified themselves via a descriptive User-Agent string referencing the academic research purpose. No scraping was performed on websites where the terms of service explicitly prohibit automated access.

The dataset does not contain personally identifiable information. Company names, job titles, and skill requirements are organizational and occupational data, not personal data. University course catalogs are published institutional records intended for public access.

All API keys used for the OpenAI translation service are stored in a local `.env` file excluded from the project repository via `.gitignore`. No credentials are embedded in code or documentation.

---

## 4.8 Scope Limitations and Dataset Constraints

### 4.8.1 University Coverage

The curriculum dataset does not represent all Armenian IT higher education institutions. Four universities were included based on data accessibility. Two significant institutions are absent:

- **National Polytechnic University of Armenia (NPUA):** NPUA operates approximately ten IT-related programs and enrols an estimated 11,000 students — making it potentially the largest technical university in Armenia by enrollment. Its official website (`polytech.am`) rejected all automated HTTP requests with HTTP 403 Forbidden errors, and a subsequent Playwright headless browser attempt was blocked by Cloudflare bot management. No structured curriculum data from NPUA was obtainable through automated or semi-automated means within the scope of this project. Its absence likely underrepresents engineering-oriented IT education in the curriculum corpus.

- **Université Française en Arménie (UFAR):** UFAR offers IT programs taught primarily in French. It was identified but not assessed within the scope of this project due to the additional translation complexity (French → English) and time constraints.

At RAU, only one of approximately eight IT-relevant programs was parsed. Master's programs in Machine Learning, Information Security, and System Programming were identified as potentially relevant but were not included.

These exclusions mean the curriculum side of the analysis reflects approximately 50–60% of accessible Armenian IT higher education programs (see `docs/data_gaps_and_limitations.md` for full documentation).

### 4.8.2 Job Market Coverage

The job dataset is a cross-sectional snapshot of postings active in Armenia during March 2026. It does not capture seasonal variation in hiring demand, longitudinal trends in skill requirements, or jobs that were posted and filled before the collection date. The broad market snapshot contains 1,369 postings from 14 sources, while the downstream IT-only subset contains 753 postings. The company-portal segment is sufficient for aggregate analysis but does not support individual company-level conclusions for smaller employers with only a handful of postings.

### 4.8.3 Translation Quality

Machine translation introduces the possibility of terminology errors in the YSU-derived curriculum data. While manual validation confirmed acceptable quality for the 50-row sample, systematic errors in the translation of specialized Armenian computing terminology cannot be fully excluded. The ESCO normalization step (Section 4.5.3) partially mitigates this risk by matching based on semantic similarity rather than exact string matching, providing robustness to surface-form variation. The original Armenian text is preserved in the dataset for independent verification.

### 4.8.4 IT Scope Definition

The scope filter applied to YSU data retained 13 programs and excluded 6 non-IT programs (Finance, Management, Economics at Bachelor and Master levels). Programs at the intersection of computing and other fields — such as "Applied Statistics and Data Science," "Data Science in Business," and "Data Processing in Physics and Artificial Intelligence" — were retained under their actual program names following URL-based verification. The IT boundary is defined as: any program whose primary focus includes computer science, informatics, information systems, information security, software engineering, data science, applied mathematics with computational focus, or closely related fields. This definition is consistent across all four universities.

---

**Chapter references:** [4] Almaleh et al. (2019) · [9] Grootendorst (2020) · [10] Zhang et al. (2022) · [11] Reimers & Gurevych (2019) · [12] Wang et al. (2020) · [14] European Commission (2023) · [15] Chiarello et al. (2021) · [17] Carbonell & Goldstein (1998) · [18] OpenAI (2024) · [19] Pedregosa et al. (2011) · [20] Gilardi et al. (2023) · [21] He et al. (2024)
