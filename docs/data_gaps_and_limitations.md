# Data Gaps and Limitations

*Generated: 2026-03-22. Updated: 2026-03-24 (final thesis dataset counts synchronized; notebook paths refreshed). For use in thesis Chapter 3 (Methodology) and Chapter 4 (Data Description).*

---

## 1. Universities with Usable Data

The following universities have structured, course-level curriculum data included in the dataset:

| University | Programs | Courses | Source | Language |
|---|---|---|---|---|
| Yerevan State University (YSU) | 13 IT programs | 691 | Web scrape (Apify, markdown) | Armenian |
| American University of Armenia (AUA) | 7 programs | 249 | Web scrape (Apify, course catalog) | English |
| National University of Architecture and Construction of Armenia (NUACA) | 4 programs | 174 | Web scrape (Apify, plain text) | English |
| Russian-Armenian University (RAU) | 1 program | 47 | PDF study plans (manual download + PyPDF2) | Russian → English |
| **Total** | | **1,161** | | |

> **Note on YSU filtering:** YSU raw scraping captured 19 program pages across multiple faculties. After applying the IT-scope filter, 13 programs (820 courses) were retained. Six programs were excluded: Finance (Bachelor + Master), Management (Bachelor + Master), and Economics (Bachelor + Master). All other YSU programs — including those whose official speciality codes fall under Physics, Statistics, or Financial Mathematics faculties — were retained under their actual program names (e.g. "Data Processing in Physics and Artificial Intelligence", "Applied Statistics and Data Science", "Blockchain and Digital Currencies").

### Notes on included universities

**YSU:** Data collected from 5 faculties/institutes: Faculty of Informatics and Applied Mathematics (Faculty 85), Faculty of Mathematics and Mechanics (Faculty 516), Institute of Physics (Faculty 525), Faculty of Economics and Management (Faculty 78), and the Information Technologies Educational and Research Center (Faculty 520 — hosts IT and Information Systems Master programs). Three program pages (programs 310, 311, 354) returned HTTP 404 from the YSU website — these are treated as inactive/placeholder entries. All currently active IT programs across the scraped faculties are confirmed covered.

**Important:** YSU program naming required careful correction. The Apify scraper captured official Armenian speciality codes (e.g. "056201 — Statistics", "055101 — Physics", "031101 — Economics") which do not reflect the actual program titles. URL-based mapping against the manually collected reference dataset was used to assign correct English program names. For example: speciality "056201.04.7" at faculty 516 is the "Applied Statistics and Data Science" Master program, not a generic Statistics degree; speciality "031101.19.7" at faculty 78 is "Data Science in Business", not Economics.

**AUA:** The course catalog at `cse.aua.am/courses/` provides a complete, structured listing of all AUA programs including course codes, full English descriptions, prerequisites, and credits. This is the richest dataset in terms of metadata per course.

**NUACA:** Four IT-related programs in the Faculty of Management and Technology are included in the final analysis dataset. Additional non-IT programs (Economics, Accounting, Logistics, Construction Management) were identified but excluded as out of scope.

**RAU:** Only the Applied Mathematics and Informatics bachelor program (01.03.02) was parsed. This was the entry point identified during initial data collection. Additional programs were discovered during final validation (see Section 2).

---

## 2. Universities with Partial or No Accessible Curriculum Data

---

### University: Russian-Armenian University (RAU) — Partial Coverage

**Status: Partially included. Coverage is limited to 1 of ~9 IT-relevant programs.**

Programs identified (all with downloadable PDF study plans at `impht.rau.am` and `rau.am/sveden/education/eduop`):

**Bachelor's programs (in addition to our existing data):**

| Program | Code | Relevance | PDF accessible |
|---|---|---|---|
| ~~Applied Mathematics and Informatics~~ | 01.03.02 | Core IT | ✓ — already in dataset |
| Infocommunication Technologies and Communication Systems | 11.03.02 | IT-adjacent | ✓ |
| Electronics and Nanoelectronics (Quantum Informatics profile) | 11.03.04 | Borderline | ✓ |
| Design and Technology of Electronic Devices | 11.03.03 | Hardware/borderline | ✓ |

**Master's programs (none currently in dataset):**

| Program | Code | Relevance | PDF accessible |
|---|---|---|---|
| Information Security (Защита информации) | 01.04.02 | Core IT | ✓ — years 1–2 at `imi.rau.am/uploads/` |
| System Programming (Системное программирование) | 01.04.02 | Core IT | ✓ — years 1–2 |
| Machine Learning (Машинное обучение) | 01.04.02 | Core IT / AI | ✓ — years 1–2 |
| Distributed Systems (Распределённые системы) | not confirmed | Core IT | ✓ — year 1 |
| Infocommunication Technologies — Wireless Comms and Sensors | 11.04.02 | IT-adjacent | ✓ — years 1–2 at `rau.am/uploads/` |
| Mathematical Modeling (Математическое моделирование) | 01.04.02 | Borderline | ✓ — years 1–2 |

**Issue:**
PDFs are downloadable but require parsing using PyPDF2 or similar tools. The RAU PDF format is a Russian-language tabular study plan, requiring regex extraction and English translation. This parsing pipeline was applied to the existing 01.03.02 program but not yet extended to the additional programs. Time and scope constraints during data collection phase prevented full coverage.

**Attempted sources:**
- `https://impht.rau.am/program/bachelor`
- `https://impht.rau.am/program/master`
- `https://rau.am/sveden/education/eduop`

**Decision:**
- The bachelor program 01.03.02 (Applied Mathematics and Informatics) is representative of the core RAU IT curriculum.
- Additional programs are noted as identified and potentially scrapeable.
- Include in extended analysis if time permits; otherwise justify exclusion in thesis as a resource constraint.
- **Do not include in current analysis.** Dataset is frozen at 1,161 courses for the purposes of this thesis.

**Recommended action if extending:**
- Download PDF study plans for 11.03.02 (bachelor) and Information Security, ML, System Programming Master programs
- Reuse existing RAU PDF parsing pipeline from `notebooks/2_collection_university/01_university_pipeline.ipynb`
- Add English translations via existing translation step

---

### University: National Polytechnic University of Armenia (NPUA / polytech.am)

**Status: Not included. Course-level data is inaccessible via automated means.**

**Institute responsible for IT programs:**
NPUA's IT programs are housed in two units:
- **Institute of Information and Telecommunication Technologies and Electronics (ICTE)** — formed 2017 from merger of former Faculties of Computer Systems and Informatics, Cybernetics and Radio Engineering, and Communication Systems.
- **Faculty of Applied Mathematics and Physics** — hosts the Informatics and Applied Mathematics program.

**Programs identified** (confirmed from indexed program pages at `polytech.am/en/edu/`):

| Program | Degree | Notes |
|---|---|---|
| Informatics (Computer Science) | Bachelor + Master | ICTE |
| Software Engineering | Bachelor + Master | Internationally accredited; some English instruction |
| Computer Engineering | Bachelor + Master | ICTE |
| Information Security | Bachelor + Master + PhD | Instruction available in English |
| Information Technologies | Bachelor | Established 2017 |
| Information Systems | Bachelor | ICTE |
| Radio Engineering and Communications | Bachelor + Master | Incl. Telecommunications, Optical Communication, Communication Networks |
| Electronics | Bachelor | ICTE |
| Informatics and Applied Mathematics | Bachelor + Master | Faculty of Applied Mathematics and Physics |
| Automation | Bachelor | Robotics / automated control systems |

This represents approximately **8–10 distinct IT-related degree programs** at NPUA.

**Issue:**
The official website (`polytech.am`) returns **HTTP 403 (Forbidden)** for all automated HTTP requests from non-Armenian IP addresses. This affects all pages including `/en/`, `/am/`, `/hy/`, and even PDF files in the `shared-files/` directory. While study plan PDFs are known to exist on the server (their URLs are indexed by search engines), they cannot be downloaded via automated tools. The PDFs appear to be in Armenian.

Program pages on `polytech.am/en/edu/` are in English but contain only **competency/learning outcome descriptions** — no course-by-course listings with credits are published in accessible HTML.

**Attempted sources and results:**
- `https://polytech.am/` → HTTP 403
- `https://polytech.am/en` → HTTP 403
- `https://polytech.am/am` → HTTP 403
- `https://polytech.am/hy/page/undergraduate-programs` → HTTP 403
- `https://polytech.am/en/edupro/` → HTTP 403 (educational programs index)
- `https://polytech.am/edupro/information-technology/` → Cloudflare bot challenge (2026-03-22); page visible in browser but Playwright headless browser blocked by Cloudflare managed challenge ("Just a moment..." page)
- `https://polytech.am/shared-files/` PDF links → HTTP 403
- `https://armeps.am/en/institutions/npua` → HTTP 404

**Status: Not usable for automated analysis.** The site is protected both by HTTP 403 for direct requests and by Cloudflare bot management for browser-like requests. Manual access via a real browser is possible but the program page (`/edupro/information-technology/`) would need to be copy-pasted manually.

**Recommended actions:**
- Contact NPUA's Institute of ICTE or Department of International Relations directly
- Search student/alumni networks (Telegram groups, LinkedIn) for curriculum documents or study plans
- Check if NPUA accreditation documents are filed publicly with ANQA (Armenian National Center for Professional Education Quality Assurance)
- If access to an Armenian IP is available (VPN, on-campus): retry fetching `polytech.am/shared-files/` PDFs

**Decision:**
- Excluded from dataset.
- Absence must be acknowledged as a limitation in the thesis.
- NPUA is one of the largest technical universities in Armenia (~11,000 students). Its exclusion affects the representativeness of the dataset, particularly for engineering-oriented IT education. It has more IT programs (10) than any other single university in the dataset.

---

### University: Université Française en Arménie (UFAR)

**Status: Not assessed. Not included in dataset.**

UFAR is a French-language university in Yerevan operating under a partnership with French institutions. It offers IT-related programs including Computer Science and Information Technologies, taught primarily in French. Exact program names, course structures, and credit volumes have not been assessed.

**Issue:**
UFAR was not included in the original data collection scope. Its curriculum pages have not been tested for accessibility or scrapeability. French-language instruction would require translation for skill extraction, adding an additional processing step compared to the other four universities.

**Attempted sources:** None — not assessed.

**Recommended actions:**
- Assess `ufar.am` for program and course listing pages
- If structured course data is accessible: scrape, parse, and add to dataset (add translation step for French course names)
- If not accessible: contact UFAR's academic department directly

**Decision:**
- Excluded from dataset due to being out of original collection scope.
- Should be noted as a limitation — UFAR represents French-model IT education in Armenia, a perspective not covered by any of the four included universities.

---

## 3. Coverage Summary

| Metric | Value |
|---|---|
| Total universities identified with IT programs in Armenia | 6 (YSU, AUA, NUACA, RAU, NPUA, UFAR) |
| Universities with full or partial data included | 4 |
| Universities fully excluded due to inaccessibility | 1 (NPUA — HTTP 403) |
| Universities fully excluded due to scope | 1 (UFAR — not assessed) |
| Universities with partial coverage (identified gap) | 1 (RAU — 1 of ~8 IT programs) |
| Total courses in dataset (IT programs only) | 1,161 |
| YSU IT programs included / total scraped | 13 / 19 (6 non-IT removed: Finance, Management, Economics) |
| Approximate program coverage (assessed universities only) | ~65–75% of accessible Armenian IT higher-education programs |
| Approximate program coverage (including NPUA and UFAR) | ~45–55% of all Armenian IT higher-education programs |

> **Note:** "IT higher-education program" is defined here as any Bachelor or Master program at an Armenian university whose primary focus includes computer science, informatics, information systems, information security, software engineering, data science, applied mathematics with computational focus, or closely related fields. Programs in economics, management, or non-computational physics are excluded even if they contain individual IT courses.

---

## 4. Methodological Implication

*This paragraph is intended for direct reuse in the thesis (Chapter 3 or 4).*

---

The dataset underlying this study is restricted to publicly accessible, structured curriculum data from Armenian universities. While four universities — YSU, AUA, NUACA, and RAU — are represented, coverage is not exhaustive. The National Polytechnic University of Armenia (NPUA), one of the major technical institutions in Armenia, could not be included due to access restrictions on its official website: all automated HTTP requests to `polytech.am` were rejected with HTTP 403 errors, and no publicly available structured curriculum data was identified through alternative channels. The Université Française en Arménie (UFAR) was identified as a further institution offering IT programs but was not assessed within the scope of this project. At RAU, data collection was limited to one bachelor-level program (Applied Mathematics and Informatics, 01.03.02), while several additional IT-relevant programs at the same institution — including master's programs in Machine Learning, System Programming, and Information Security — were identified but not scraped.

These limitations mean that the analysis reflects the publicly accessible portion of Armenian IT higher education rather than a complete institutional census. The four included universities represent a diverse cross-section — a large state research university (YSU), an American-accredited liberal arts university (AUA), a specialized technical university in architecture and construction (NUACA), and a Russian-model research university (RAU) — providing breadth across educational philosophies and program structures. Nevertheless, the absence of NPUA and UFAR data may underrepresent engineering-oriented and French-model IT curricula respectively. Any conclusions drawn from this dataset should be understood in the context of this structural limitation, and future research should seek to obtain NPUA curriculum data through direct institutional contact or official accreditation records, and assess UFAR's course-level curriculum accessibility.

---

---

## 5. ESCO Mapping Noise and False Positives

*Identified: 2026-03-25. Based on inspection of `data/processed/esco/gap_analysis.csv` and `data/processed/esco/skill_frequency_overall.csv` (notebook 06 outputs). For use in thesis Chapter 3 (Methodology) or Chapter 5 (Results — limitations of the normalization step).*

The ESCO normalization step (notebook 05) maps extracted keyword phrases to ESCO skill concepts using cosine similarity on sentence embeddings. While this enables structured comparison across the curriculum-industry skill space, inspection of the output reveals two categories of problems: **false positive mappings** and **overly broad concepts**.

---

### 5.1 Clear False Positive Mappings

These ESCO labels appear in job skill outputs but are semantically unrelated to the actual content that triggered them. They result from the embedding model finding surface-level or contextual similarity to the wrong concept.

| ESCO concept matched | Appears in | Actual source phrase | Why it's wrong |
|---|---|---|---|
| `work with playwrights` | 8 job docs (1.1%) | "Playwright" (Microsoft browser testing framework) | ESCO concept refers to theatre; Playwright the tool shares the word but is a JavaScript E2E testing library |
| `woodworking tools` | 7 job docs (1.0%) | "tools" in developer context (dev tools, CLI tools, testing tools) | ESCO concept refers to physical craft/carpentry tools |
| `sell tickets` | 5 job docs (0.7%) | Ticketing systems (JIRA tickets, support tickets, incident tickets) | ESCO concept refers to selling event/transport tickets |
| `scan photos` | 4 job docs (0.6%) | Image/camera API or photo processing mentions | ESCO concept is about document/photo scanning as a clerical task |
| `property law` | 3 job docs (0.4%) | Likely from real-estate-tech company descriptions | Legal concept unrelated to IT skills |
| `Scratch` | 10 job docs (2.2%) | "from scratch" in job descriptions ("build from scratch", "develop from scratch") | ESCO maps this to Scratch, the visual block-based programming language for children |

**Most notable case for thesis:** The `work with playwrights` → Playwright mapping is the clearest illustration of a fundamental limitation of embedding-based ESCO normalization: the model cannot distinguish between a proper noun (a software tool named "Playwright") and the common noun ("playwright" as a profession). This is a known challenge for domain-specific technical vocabulary where tool names overlap with natural language words.

---

### 5.2 Overly Broad ESCO Concepts

These concepts are technically correct matches but are so general that their high frequency inflates alignment scores without adding meaningful signal. They function more as noise than as informative skill indicators.

| ESCO concept | Frequency | Issue |
|---|---|---|
| `ICT project management methodologies` | 89 job docs (19.5%) | Catches any mention of Agile, Scrum, Kanban, sprint, or roadmap — present in almost every tech job posting |
| `ICT system programming` | 54 job docs (11.8%) | Broad catch-all for any systems/low-level programming context; maps to OS internals, drivers, architecture, and general "programming" mentions alike |
| `computer programming` | 36 job docs (7.9%) | Too generic to distinguish any specific skill |
| `process data` | 29 job docs (6.4%) | Covers any data handling mention; maps indistinguishably to ETL pipelines, analytics, and casual data use |
| `digital data processing` | 28 job docs (6.1%) | Same problem as above; overlaps heavily with `process data` |
| `automation technology` | 23 job docs (5.0%) | Aggregates CI/CD pipelines, test automation, RPA, and industrial automation under one label |
| `implement ICT recovery system` | 10 job docs (2.2%) | Triggered by backup, disaster recovery, or business continuity mentions; the ESCO label implies a more specific implementation task |

**Implication for coverage percentages:** The high frequencies of `ICT project management methodologies` and `ICT system programming` in particular mean that alignment coverage scores (e.g., 10–12% for AUA Computer Science) may be partially inflated by these coarse concepts. Programs that include any project management or general programming content will match these regardless of actual technical depth alignment.

---

### 5.3 Contextually Ambiguous Matches

These concepts appear in the outputs and are not wrong, but require context to interpret correctly.

| ESCO concept | Frequency | Context |
|---|---|---|
| `betting` | 7 job docs (1.0%) | Legitimate — SoftConstruct and BetConstruct are Armenian betting/gaming software companies; their job descriptions genuinely relate to betting platform development |
| `banking activities` | 10 job docs (1.4%) | Fintech roles in the dataset; ESCO label is accurate but sounds non-technical out of context |
| `develop animations` / `principles of animation` | 6 + 5 job docs | Possibly legitimate for UI/frontend roles (CSS animations, Lottie, etc.) but could also be false matches from unrelated content |

---

### 5.4 Recommended Thesis Framing

When reporting ESCO-normalized alignment results, acknowledge:

1. **Embedding-based mapping does not handle proper nouns reliably.** Technical tool names (Playwright, Scratch, Docker, React) are sometimes mismatched to unrelated ESCO concepts when the word has a common-language meaning. A post-filtering step using a curated IT tool lexicon would reduce this noise.

2. **ESCO concept granularity is uneven.** Some concepts (e.g., `Python`, `Java`, `DevOps`) map cleanly to specific technologies. Others (`ICT system programming`, `computer programming`) are so broad they add little discriminative value to alignment analysis.

3. **Coverage percentages should be interpreted as lower bounds with caveats.** False positives inflate the overlap count, while the broad concepts make it harder to distinguish deep from shallow alignment.

---

*Last updated: 2026-03-25*
