# Chapter 2: Literature Review

*[DRAFT STATUS — substantive skeleton. Send to Gemini for tone/flow polish after review.]*

---

## 2.1 The Curriculum–Labor Market Gap: An Established Problem

The mismatch between what universities teach and what employers need is not a new observation. It has been documented across regions and disciplines for decades, and it takes two analytically distinct forms. The first is *overeducation*: workers hold credentials that exceed the formal requirements of their positions. The second is *skill mismatch*: workers lack specific technical or practical competencies despite holding formally relevant degrees. Both can coexist, and in post-Soviet transition economies they frequently do (Kupets, 2016).

The scale of the problem has attracted growing research attention. Aljohani et al. (2022) conducted a systematic review of 10,214 Scopus-indexed records published between 2010 and 2021 on curriculum–labor market alignment, finding a marked increase in publication volume after 2015, driven primarily by the availability of large-scale job posting datasets and advances in natural language processing. Their review identifies three dominant methodological clusters in the field: survey-based employer feedback studies, competency framework mapping exercises, and, most recently, computational corpus analysis studies. The present thesis belongs to the third cluster, which the authors identify as the fastest-growing and methodologically most rigorous approach.

A consistent finding across all three clusters is that the gap is not uniformly distributed. Certain skill categories — particularly those at the intersection of applied computing, data analysis, and communication — appear persistently under-represented in curricula relative to their labor market demand. At the same time, curricula in countries with centralized or historically rigid degree structures tend to carry a surplus of theoretical content that has limited direct employer relevance (Kupets, 2016; Amirova & Valiyev, 2021).

---

## 2.2 Computational Approaches to Curriculum Alignment

The shift toward computational methods for curriculum alignment analysis was made possible by two parallel developments: the digitization of university course catalogs and the mass availability of structured job posting data from platforms such as LinkedIn and national job boards. These developments enabled researchers to treat curricula and job advertisements as comparable text corpora and apply information retrieval and NLP techniques to quantify alignment at scale.

The most methodologically proximate study to the present thesis is Almaleh et al. (2019), who propose a framework — which they term "Align My Curriculum" — for comparing university course syllabi against job postings from a Saudi Arabian employment portal. Their pipeline combines Naive Bayes text classification with cosine similarity scoring to produce per-course alignment scores and an aggregate institution-level alignment index. Applying this to computing faculties in Saudi Arabia, they find alignment rates below 50% for several programs, with particular deficits in software engineering and data management skills. This study establishes the two-dataset comparative design — one curriculum corpus, one job market corpus — that the present thesis adopts and extends.

The key extensions in the present thesis relative to Almaleh et al. (2019) are threefold. First, the job market dataset here spans 11 sources combining aggregators and direct employer portals, whereas Almaleh et al. draw from a single portal. Second, the present study handles multilingual input data — Armenian, English, and Russian — while Almaleh et al. operate entirely in English. Third, the skill normalization step here uses the ESCO taxonomy, providing a standardized, internationally recognized vocabulary for reporting gap findings.

A parallel line of work was presented at the 15th International Conference on Educational Data Mining (EDM 2022). Ahadi, Kitto, Rizoiu, and Musial (2022) — in a poster paper titled "Skills Taught vs Skills Sought: Using Skills Analytics to Identify the Gaps between Curriculum and Job Markets" — apply skills analytics to both curriculum documents and job postings to identify skill gaps in a directly comparable framing to the present thesis (DOI: 10.5281/zenodo.6853121).

More recently, Musazade, Mezei, and Zhang (2026) introduce the UniSkill dataset, which links university course descriptions to ESCO skills for Systems Analyst and Management Analyst occupations, providing a benchmark for curriculum-to-taxonomy matching. While the occupational scope of UniSkill differs from the present study, its methodology — mapping curriculum text to ESCO concepts via embedding similarity — validates the core approach used here. UniSkill was accepted to the Language Resources and Evaluation Conference (LREC 2026); the arXiv preprint is available at arXiv:2603.03134.

---

## 2.3 NLP Methods for Skill Extraction

Extracting skills from unstructured text is a non-trivial NLP task. Job descriptions and course names are typically short, domain-specific, and written in varied stylistic registers. Two broad paradigms exist for this task: unsupervised keyword extraction and supervised sequence labeling.

In the unsupervised paradigm, methods such as TF-IDF and RAKE identify candidate skill phrases based on statistical salience within a document corpus. A more powerful approach in this category is KeyBERT (Grootendorst, 2020), which uses BERT-based sentence embeddings to identify the candidate phrases most semantically similar to the document as a whole. KeyBERT requires no labeled training data, is applicable to short texts, and supports multilingual models — making it well-suited to the curriculum data in this study, where course descriptions are often one or two sentences in length.

The supervised paradigm treats skill extraction as a named entity recognition (NER) problem: a model is trained to label spans of text as skill entities or non-entities. Zhang et al. (2022) introduce SkillSpan, a dataset of 14,759 annotated sentences from job postings, and fine-tune transformer-based models on it to produce a state-of-the-art skill extraction system. SkillSpan achieves substantially higher precision on English job posting data than unsupervised alternatives, at the cost of being language- and domain-specific.

For the present thesis, two unsupervised approaches are implemented and compared: TF-IDF keyword extraction and KeyBERT. KeyBERT uses the `all-MiniLM-L6-v2` sentence transformer (Wang et al., 2020) applied to both curriculum records and job postings, given its suitability for short texts and computational efficiency for large-scale corpus processing. All curriculum text is available in English after translation (Section 4.4), making an English-only model sufficient. The sentence embedding architecture underlying KeyBERT builds on Reimers and Gurevych (2019), which produces fixed-length sentence representations optimized for semantic similarity tasks. SkillSpan represents the state-of-the-art in supervised skill extraction and is cited here as the benchmark that unsupervised methods are measured against in the literature, but its use requires labeled training data that was not available for Armenian curriculum texts and therefore falls outside the scope of this study.

A persistent challenge in skill extraction is the distinction between a *skill* (a competence a person can possess) and a *topic* or *requirement* mentioned in context. A job posting that mentions "microservices architecture" may be describing a system the candidate will work with rather than a skill they must possess. This ambiguity is inherent to the task and cannot be fully resolved by automated methods alone. The methodology section (Chapter 4) documents the quality validation steps taken to assess and partially address this issue.

---

## 2.4 Skill Taxonomies as Measurement Frameworks

Extracted skill phrases, in their raw form, are not directly comparable across sources: a job posting may demand "Python scripting," a course may teach "programming in Python," and a taxonomy may list "Python (programming language)" — these are semantically equivalent but textually distinct. A shared taxonomy is therefore necessary to normalize extracted phrases to a common vocabulary before any alignment comparison can be made.

Three taxonomies are relevant to this study: ESCO, O*NET, and SFIA.

**ESCO** (European Skills, Competences, Qualifications and Occupations) is a multilingual taxonomy developed by the European Commission. It currently comprises 3,039 occupation concepts and 13,939 skill and competence concepts, organized in 28 languages (European Commission, 2023). ESCO was explicitly designed to serve as an interface between the education and employment systems — its conceptual architecture links occupations to the skills they require and qualifications that support entry into them. This design philosophy makes ESCO the most appropriate primary taxonomy for a study that bridges curricula and job market data. Furthermore, Armenian universities operate within the Bologna Process framework, which is the European higher education architecture that ESCO was built to complement.

ESCO has known limitations. Chiarello et al. (2021) demonstrate that ESCO coverage of Industry 4.0 skills — including IoT, AI applications, and robotics — lags significantly behind actual industry practice, due to the taxonomy's update cycle. For the present study, this means that recent or niche skills found in job postings from cutting-edge companies (such as prompt engineering, LangChain, or specific cloud service APIs) will not match any ESCO concept. Rather than treating this as a failure of the methodology, these unmatched terms are retained as a separate "emerging skills" category, which itself constitutes a finding: they represent the fastest-moving frontier of IT skill demand that formal taxonomies have not yet absorbed.

**O*NET** (Occupational Information Network) is the U.S. Department of Labor's occupational taxonomy, providing structured descriptors for approximately 1,000 occupations. While O*NET's occupational detail exceeds ESCO's in some areas, its U.S.-centric framing and lack of multilingual support make it less appropriate as the primary taxonomy for an Armenian study. It is referenced here as a secondary cross-validation tool: where findings map to identifiable O*NET skill categories, this is noted to improve accessibility for international readers.

**SFIA** (Skills Framework for the Information Age) is an IT-specific professional skills framework that organizes 121 technical and managerial skills across seven levels of responsibility (SFIA Foundation, 2021). Unlike ESCO and O*NET, SFIA is designed exclusively for the IT profession. While it does not provide an accessible API or downloadable dataset that supports programmatic matching at scale, its seven-level responsibility structure — ranging from "Follow" (level 1) to "Set strategy" (level 7) — is used in the discussion chapter to characterize the *type* of skill gap identified: whether universities are teaching the right skills at the wrong level, or missing skill categories entirely.

---

## 2.5 The Armenian and Post-Soviet Educational Context

Understanding the nature of any curriculum–labor market gap in Armenia requires engagement with the structural conditions of Armenian higher education, which cannot be read off from comparative studies conducted in Western European or North American contexts.

Armenia's higher education system is a product of the Soviet institutional architecture: centralized degree structures, strong theoretical emphasis, weak differentiation between research and teaching functions, and limited responsiveness to labor market signals (Kupets, 2016). Following independence in 1991, Armenia underwent a series of reform attempts, including formal accession to the Bologna Process in 2005. Bologna adoption introduced the two-cycle degree structure (Bachelor/Master), European Credit Transfer System (ECTS) compatibility, and a formal commitment to learning-outcome-based curriculum design. However, adoption has been uneven: the degree structure has largely been implemented, but outcome-based curriculum design and employer-facing program review remain less consistently embedded in practice (Kupets, 2016).

Kupets (2016) provides the most directly relevant empirical evidence for the Armenian context, drawing on World Bank STEP household survey data. Key findings include: approximately 30% of urban Armenian workers are overeducated for their positions; 69.9% of overeducated workers report their formal education has limited practical usefulness; and the IT sector specifically reports thousands of unfilled vacancies despite high numbers of computing graduates. Kupets frames this as a structural mismatch — not a failure of individual graduates — rooted in the Soviet-era curriculum's emphasis on abstract theoretical knowledge over applied technical competence. This framing directly motivates the present study: if the gap is structural, it can only be diagnosed and addressed through structural data, not through individual graduate surveys.

The Armenian IT sector has expanded substantially since the period studied by Kupets. Major international companies have established development centers in Yerevan (EPAM, SoftConstruct, ServiceTitan), domestic technology companies have scaled internationally (Picsart, Krisp), and diaspora investment has seeded a range of startups and accelerators. This expansion has increased both the volume and the specificity of employer skill demands in the local market, potentially widening the curriculum gap documented in earlier survey research. The present thesis provides a contemporaneous, data-driven update to that earlier evidence base.

The closest regional academic comparator is Amirova and Valiyev (2021), who study the competence gap in Azerbaijan — a former Soviet republic with close structural and cultural similarity to Armenia in its higher education system. Their survey-based study of 24 competences finds sharp disagreement between employers and graduates on which competences are most important: employers prioritize practical technical skills and communication, while graduates overestimate the value of formal theoretical credentials. This pattern is consistent with the structural account offered by Kupets and provides a qualitative benchmark against which to interpret the quantitative findings of the present study.

---

## 2.6 Constructive Alignment and the Theoretical Case for Measurement

The concern with curriculum–labor market alignment has a well-developed theoretical base in educational research. Biggs and Tang (2011) introduce the concept of *constructive alignment* — the principle that effective teaching requires internal coherence between three elements: intended learning outcomes (ILOs), teaching and learning activities, and assessment tasks. A curriculum in which assessments do not test what the ILOs specify, or in which teaching activities do not lead students toward the stated outcomes, is structurally misaligned even before any external labor market comparison is made.

Biggs and Tang developed constructive alignment primarily as a framework for internal curriculum quality. However, the same logic extends naturally to external alignment: if ILOs are to be educationally meaningful, they should reflect competences that graduates will actually use in professional life. When a systematic gap exists between what a curriculum declares it teaches and what employers need graduates to know, the external misalignment is often a symptom of an earlier failure to define ILOs with reference to any external standard.

In the context of Armenian universities, this connection is particularly relevant. As noted above, outcome-based curriculum design has been formally adopted as part of Bologna compliance, but implementation is uneven. For several universities in this study — notably YSU, whose course data provides names but limited or no description fields — the absence of published ILOs means that skill content must be inferred entirely from course names. This is a methodological constraint, but also a diagnostic signal: programs whose curricula cannot be analyzed because learning outcomes are not documented are the same programs most likely to be misaligned with labor market expectations.

The operationalization of "skills" in this thesis follows the task-based framework introduced by Autor, Levy, and Murnane (2003). In their model, occupations are characterized by the tasks they require — cognitive or manual, routine or non-routine — and the value of skills is defined by which tasks they enable. This framework underpins the use of job posting text as a proxy for skill demand: a job description specifies the tasks an employer needs performed, and the skills listed or implied in that description are those that enable task completion. ESCO, as the normalization target for extracted skills, encodes this task-skill relationship: each ESCO skill concept is linked to the occupations whose tasks it supports.

---

## 2.7 Summary and Research Gap

The literature reviewed in this chapter establishes three points that motivate the present thesis. First, curriculum–labor market misalignment is a documented and consequential problem, particularly in post-Soviet transition economies where structural path dependency limits curriculum responsiveness to changing employer demand. Second, computational alignment analysis using NLP and skill taxonomies is an established and growing methodology with several published precedents, the most closely related being Almaleh et al. (2019). Third, no prior study has applied this methodology to the Armenian context, and the existing evidence base for Armenia relies on survey-based data that is now a decade old.

This thesis fills that gap by constructing the first large-scale, multi-source, computationally analyzed curriculum–job market alignment dataset for Armenian IT higher education, and by applying a reproducible NLP pipeline to quantify the skill gap at program and institution level.

---

*Citation checklist for this chapter:*
- *Kupets (2016) — IZA World of Labor, verified ✓*
- *Aljohani et al. (2022) — Journal of Innovation & Knowledge, verified ✓*
- *Almaleh et al. (2019) — Sustainability, verified ✓*
- *Ahadi, Kitto, Rizoiu & Musial (2022) — EDM 2022 poster, DOI: 10.5281/zenodo.6853121 — verified ✓*
- *Musazade, Mezei & Zhang (2026) — UniSkill, arXiv 2603.03134, accepted LREC 2026 — verified ✓*
- *Grootendorst, M. (2020) — KeyBERT, Zenodo software release, DOI: 10.5281/zenodo.4461265 — verified ✓ (cite as @misc Zenodo, not journal)*
- *Zhang et al. (2022) — SkillSpan, NAACL, verified ✓*
- *Reimers & Gurevych (2019) — Sentence-BERT, EMNLP, verified ✓*
- *European Commission (2023) — ESCO documentation — add URL in references*
- *Chiarello et al. (2021) — Technological Forecasting and Social Change, verified ✓*
- *SFIA Foundation (2021) — sfia-online.org — add URL in references*
- *Amirova & Valiyev (2021) — Journal of Teaching and Learning for Graduate Employability, verified ✓*
- *Biggs & Tang (2011) — Teaching for Quality Learning, verified ✓*
- *Autor, Levy & Murnane (2003) — Quarterly Journal of Economics, verified ✓*
