# Presentation Source — Thesis Progress Presentation

*Purpose:* This document is written as a source file for slide-generation tools such as NotebookLM or Gamma.

*Audience:* Thesis professor / academic review audience.

*Presentation goal:* Show what has been done so far, explain the pipeline clearly, present current results honestly, and highlight the remaining limitations and next steps.

*Important framing:* This is a work-in-progress research presentation, not a final defense.

---

## Slide 1 — Title

**Title:** Armenian IT Curriculum - Labor Market Alignment

**Subtitle:** Master's Thesis Progress Presentation

**Presenter:** Liana Aghamalyan

**Institution:** YSU

**Status:** Work in progress, current state as of March 2026

**Speaker note:**
This presentation shows the full research pipeline built so far, the current results, the main limitations, and the next steps before the pre-final version of the thesis.

---

## Slide 2 — Research Question

**Main research question:**
How well do IT curricula from selected Armenian universities align with current Armenian IT labor market demands?

**Why this matters:**
- Universities need evidence-based curriculum updates
- Employers report skill gaps, but the gap is usually discussed only qualitatively
- Armenia's IT sector is growing quickly, so outdated curricula become costly
- A reproducible pipeline can support repeated alignment checks in the future

**Suggested visual:**
A simple triangle or flow showing:
University curricula -> Skill extraction -> Comparison with job market

---

## Slide 3 — What This Project Contains

**Current scope of the project:**
- 4 universities
- 1,161 courses
- 25 named programs
- 1,369 collected job postings from 14 sources
- 753 IT-only postings used in downstream NLP and alignment analysis

**Universities included:**
- YSU
- AUA
- NUACA
- RAU

**Important note:**
This is not yet the full Armenian higher-education landscape.

**Suggested visual:**
Two boxes side by side:
- Education data
- Labor market data

---

## Slide 4 — Current Research Status

**Completed:**
- Data collection
- Data cleaning and structuring
- YSU translation pipeline
- IT-only job filtering
- TF-IDF extraction
- KeyBERT extraction
- Sensitivity analysis
- ESCO calibration
- ESCO normalization
- Final alignment analysis
- Thesis draft in progress

**Still in progress / next:**
- Thesis polishing
- Stronger discussion chapter
- Possible extra data collection from NPUA, UFAR, and RAU

**Speaker note:**
The project already has an end-to-end analytical pipeline. What remains is improving coverage, interpretation, and final writing.

---

## Slide 5 — Full Pipeline Overview

**Pipeline:**
1. Collect curriculum data
2. Collect job-market data
3. Clean and structure both datasets
4. Filter the job market to IT-only postings
5. Translate Armenian curriculum text to English
6. Extract candidate skills with TF-IDF and KeyBERT
7. Validate and test sensitivity
8. Normalize skills to ESCO
9. Run alignment analysis
10. Interpret gaps, overlap, and limitations

**Suggested visual:**
A horizontal pipeline with arrows and 10 short labeled steps.

---

## Slide 6 — Data Collection

**Curriculum side:**

| University | Programs | Courses | Description availability |
|---|---:|---:|---|
| YSU | 13 | 691 | Yes, translated from Armenian |
| AUA | 7 | 249 | Yes, English original |
| NUACA | 4 | 174 | Mostly names only |
| RAU | 1 | 47 | Mostly names only |
| Total | 25 | 1,161 | Mixed quality |

**Job side:**
- Broad market snapshot: 1,369 postings
- 14 sources
- Aggregators plus company portals

**Key message:**
The study compares two real corpora: university curriculum text and employer demand text.

---

## Slide 7 — Job Market Collection and IT-Only Filtering

**Why filtering was needed:**
The broad market snapshot still included mixed, managerial, commercial, and non-core roles.

**IT-only filter result:**

| Decision | Count |
|---|---:|
| Keep | 753 |
| Drop | 558 |
| Review | 58 |

**Why this matters:**
- The broad snapshot is useful for transparency
- The IT-only subset is better for real skill-demand analysis
- This reduces noise from non-IT positions

**Suggested visual:**
Funnel chart:
1,369 broad jobs -> 753 IT-only jobs

---

## Slide 8 — Translation Step

**Problem:**
YSU curriculum content is in Armenian, while the job-market corpus is mostly English.

**Chosen solution:**
Translate Armenian curriculum text to English first, then run one shared English-language pipeline.

**Why this choice was made:**
- Easier to validate manually
- Easier to explain in the thesis
- Easier to compare directly with English job postings

**Provider comparison:**

| Provider | Result |
|---|---|
| OpenAI gpt-4o-mini | 20/20 |
| Perplexity Sonar Pro | 6/20 |

**Key message:**
Translation was treated as a methodological decision, not as a black box.

---

## Slide 9 — Preprocessing and Cleaning

**Main cleaning steps:**
- Boilerplate removal from repeated job-posting sections
- Custom stopword filtering
- Company-name filtering
- Generic English noise filtering
- Multi-word noise phrase filtering
- Skill-likeness post-filter

**Why this was necessary:**
Without cleaning, many extracted "skills" were actually generic words such as:
- access
- activities
- challenges
- environment

**Key message:**
The project did not accept raw NLP output blindly. Cleaning and quality control were essential.

---

## Slide 10 — TF-IDF Method

**What TF-IDF does:**
TF-IDF finds words or phrases that are important inside one document compared to the whole corpus.

**Simple formula:**
TF-IDF(term, document) = term frequency in the document x inverse document frequency in the corpus

**Why TF-IDF was used:**
- Strong baseline
- Transparent and easy to explain
- Works well for repeated technical vocabulary
- Performed better than KeyBERT in validation

**Simple interpretation:**
Words that appear often in one document but not everywhere get higher importance.

---

## Slide 11 — TF-IDF Example on My Data

**Example course:**
Information Technologies in the Professional Field (Python)

**Top TF-IDF outputs:**
- python
- data
- language data variables
- arrays functions
- language data

**What this shows:**
TF-IDF captured the main topic well, especially the core technology word `python`.

**Strength:**
Good at extracting shared technical vocabulary.

**Weakness:**
Can still produce awkward fragments or too-general terms.

---

## Slide 12 — KeyBERT Method

**What KeyBERT does:**
KeyBERT uses embeddings to find phrases that are semantically close to the whole document.

**Simple formula:**
Cosine similarity between:
- document embedding
- candidate phrase embedding

**Why KeyBERT was used:**
- To compare a semantic method against TF-IDF
- To capture meaningful phrases, not only frequent terms
- To test whether semantic extraction improves alignment

**Key message:**
KeyBERT is more semantic, but not necessarily better for this dataset.

---

## Slide 13 — KeyBERT Example on My Data

**Same course example:**
Information Technologies in the Professional Field (Python)

**Top KeyBERT outputs:**
- data visualization python
- visualization python teaching
- fundamentals python
- python teaching
- teaching create visualizations

**What this shows:**
KeyBERT produces richer phrases than TF-IDF.

**But the problem is:**
These phrases often do not match job phrases directly as strings, even when they refer to similar skills.

**Key message:**
KeyBERT is useful, but raw overlap is very low before normalization.

---

## Slide 14 — Comparison Before ESCO Normalization

**Pre-ESCO results:**

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum unique skills | 3,442 | 4,812 |
| Job unique skills | 3,153 | 5,530 |
| Overlap | 279 | 18 |
| Coverage rate | 8.85% | 0.33% |

**Interpretation:**
- TF-IDF performs much better on raw string overlap
- KeyBERT extracts richer phrases, but they rarely match exactly
- Raw string overlap strongly underestimates real conceptual overlap

**Suggested visual:**
Small bar chart: pre-ESCO coverage rates

---

## Slide 15 — Validation and Sensitivity Analysis

**Three validation checks were done:**

1. **Description asymmetry test**
   AUA with names only vs names + descriptions

2. **Validation against human-curated skills_tags**
   151 job postings from Staff.am and EPAM

3. **Noise audit**
   Found and removed many generic non-skill words

**Important validation result:**

| Measure | TF-IDF | KeyBERT |
|---|---:|---:|
| Soft recall vs human skills_tags | 44% | 21% |

**Key message:**
The methods are imperfect, but they were tested instead of being trusted automatically.

---

## Slide 16 — Why ESCO Normalization Was Needed

**Problem before normalization:**
Different phrases can refer to the same concept.

**Examples:**
- python programming
- python development
- programming in python

These may all describe the same real skill, but string matching treats them as different.

**Solution:**
Map extracted phrases to ESCO concepts.

**What ESCO is:**
European Skills, Competences, Qualifications and Occupations taxonomy.

**Key message:**
ESCO allows apples-to-apples comparison between curriculum language and employer language.

---

## Slide 17 — ESCO Matching and Calibration

**How matching works:**
1. Encode extracted phrases
2. Encode ESCO labels
3. Compare by cosine similarity
4. Keep matches above a calibrated threshold

**Threshold calibration:**

| Item | Value |
|---|---|
| Calibration pairs | 293 |
| Selected threshold | 0.75 |
| Best F1 | 0.711 |
| Human spot-check agreement | 94.3% on 35 pairs |

**Key message:**
The threshold was not arbitrary. It was tested empirically.

---

## Slide 18 — ESCO Example on My Data

**Example idea:**

| Raw phrase | ESCO concept |
|---|---|
| python programming | Python (programming language) |
| python development | Python (programming language) |
| object oriented programming | object-oriented programming |
| OOP principles | object-oriented programming |

**What changes after normalization:**
Different surface forms can now count as the same concept.

**Key message:**
This is the step that turns vocabulary overlap into concept overlap.

---

## Slide 19 — Results After ESCO Normalization

**Post-ESCO results:**

| Metric | TF-IDF | KeyBERT |
|---|---:|---:|
| Curriculum ESCO concepts | 332 | 398 |
| Job ESCO concepts | 326 | 207 |
| Overlap | 107 | 59 |
| Coverage rate | 32.82% | 28.5% |
| Gap | 219 | 148 |
| Surplus | 225 | 339 |

**Interpretation:**
- ESCO normalization raises coverage strongly
- TF-IDF remains the stronger main method
- KeyBERT becomes much more useful after normalization

**Suggested visual:**
Before vs after bar chart for both methods

---

## Slide 20 — Emerging Tech Layer Beyond ESCO

**Problem:**
ESCO v1.2 misses many modern IT tools.

**Examples missing or poorly represented in ESCO:**
- Docker
- React
- Azure
- Kubernetes
- TypeScript
- CI/CD

**So an extra direct tech lexicon was added.**

**Examples from current demand data:**

| Skill | Job docs | Curriculum docs | Status |
|---|---:|---:|---|
| Microsoft Azure | 35 | 0 | Gap |
| React | 30 | 0 | Gap |
| LLM / GenAI | 25 | 4 | Overlap |
| Node.js | 20 | 3 | Overlap |
| Amazon Web Services | 20 | 0 | Gap |

**Key message:**
The main ESCO metric is useful, but it is still a lower bound because ESCO misses modern tools.

---

## Slide 21 — Main Current Results

**University-level average coverage:**

| University | Avg. coverage |
|---|---:|
| AUA | 8.06% |
| YSU | 5.96% |
| RAU | 2.76% |
| NUACA | 2.52% |

**Program range:**
- Best: AUA Computer and Information Science, Master - 12.27%
- Lowest: NUACA Geographic Information Systems, Master - 0.92%

**Important interpretation:**
These are not pure quality rankings, because description availability is uneven across universities.

---

## Slide 22 — Top Demanded Skills in the IT-Only Market

**Top demanded skills overall:**

| Rank | Skill | % of IT jobs |
|---:|---|---:|
| 1 | Python | 33.6% |
| 2 | CI/CD | 31.1% |
| 3 | Amazon Web Services | 29.8% |
| 4 | Microsoft Azure | 26.3% |
| 5 | Google Cloud | 24.8% |
| 6 | Docker | 22.1% |
| 7 | DevOps | 21.5% |
| 8 | Kubernetes | 21.5% |
| 9 | ICT project management methodologies | 19.5% |
| 10 | React | 16.2% |

**Key message:**
The demand side is heavily practical, cloud-oriented, and tool-oriented.

---

## Slide 23 — Gap Interpretation

**Examples of interpretable ESCO gap concepts:**
- PHP
- Java
- TypeScript
- SQL Server
- DevOps
- CSS
- Android
- responsive design

**Main interpretation:**
The curriculum is stronger on foundational knowledge than on applied workplace competences and modern production tools.

**Important caution:**
Some ESCO gap labels are noisy or too broad, so they need interpretation.

---

## Slide 24 — Knowledge vs Competence

**TF-IDF concept-type split:**

| Category | Knowledge | Skill/Competence |
|---|---:|---:|
| Overlap | 77.6% | 22.4% |
| Gap | 48.9% | 51.1% |
| Surplus | 60.4% | 39.1% |

**Interpretation:**
- Curricula overlap with the market mostly at the knowledge level
- The gap is stronger on practical competence
- This supports the idea that universities teach the right domains, but not enough applied practice

---

## Slide 25 — Main Limitations

**Current limitations:**
- NPUA not included yet
- UFAR not included yet
- RAU only partially covered
- Description asymmetry across universities
- ESCO vocabulary gap for modern technologies
- March 2026 snapshot only, not longitudinal
- Unsupervised extraction methods still have recall limits

**Most important caution for the audience:**
The current alignment figures are lower-bound estimates, not final absolute truth.

---

## Slide 26 — What I Am Doing Next

**Planned next steps:**
- Try to get in touch with NPUA to obtain curriculum data
- Try to get in touch with UFAR to include their relevant programs
- Visit or contact RAU to improve coverage beyond one program
- Continue improving the thesis draft and final interpretation

**How to say this in the presentation:**
I already have a complete working pipeline, and now I am focusing on improving dataset coverage and strengthening the final thesis discussion.

---

## Slide 27 — Project Structure and Reproducibility

**What exists already:**
- Thesis draft
- Structured datasets
- Documented methodology
- Separate notebooks by stage
- Validation and calibration outputs
- Advisor-oriented documentation

**Main message:**
This is not only a thesis text. It is a reproducible research project with a full documented pipeline.

**Suggested visual:**
Simple three-box structure:
- data
- notebooks
- thesis/docs

---

## Slide 28 — Final Takeaway

**Main conclusion at the current stage:**
Armenian IT curricula already overlap with the labor market at the knowledge level, but they lag behind on applied competences and modern tools.

**What makes this project strong already:**
- real data
- full pipeline
- validation
- transparent limitations
- actionable results

**Closing message:**
The project is already analytically complete enough to discuss seriously, while still having room to improve the dataset and the final thesis before submission.

---

## Optional Notes for Slide Generator

**Preferred presentation style:**
- Clean academic design
- Minimal text per slide
- Use visual pipeline diagrams, tables, and comparison charts
- Do not show code screenshots
- Do not invent extra results
- Keep wording simple and professional

