# Abstract

This thesis presents the first large-scale, computational analysis of the alignment between IT university curricula and labor market skill demands in Armenia. Four Armenian universities — Yerevan State University (YSU), the American University of Armenia (AUA), the National University of Architecture and Construction of Armenia (NUACA), and the Russian-Armenian University (RAU) — are examined alongside a 1,369-posting market snapshot collected from 14 sources active in Armenia in March 2026. Downstream NLP and alignment analysis use an IT-only subset of 753 postings.

A five-stage NLP pipeline is constructed: (1) data collection and structuring; (2) multilingual preprocessing including Armenian-to-English translation of 691 YSU course records; (3) automated skill extraction using TF-IDF and KeyBERT (all-MiniLM-L6-v2); (4) normalization of extracted skill phrases against the ESCO v1.2 taxonomy via cosine similarity; and (5) alignment analysis producing per-program coverage rates, gap sets, and surplus sets.

Pre-ESCO baseline results indicate a raw string overlap of 8.85% (TF-IDF) and 0.33% (KeyBERT) between curriculum and job market skill vocabularies — figures that substantially underestimate true alignment due to synonymous phrasing. After ESCO normalization, coverage rises to 32.82% (TF-IDF) and 28.5% (KeyBERT). The overlap is dominated by knowledge concepts (77.6%) over applied competences (22.4%), while the gap remains slightly competence-heavy (51.1%), indicating that curricula cover relevant subject domains but fall short on practice-oriented content. Sensitivity analyses confirm a 5× coverage advantage for programs with full course descriptions (AUA) over name-only programs (NUACA/RAU), and a 44% soft recall against human-curated skill tags from 151 job postings. Key market-demanded skills include Python, CI/CD, AWS, Azure, GCP, Docker, DevOps, Kubernetes, React, and .NET / C#; interpretable ESCO gap concepts include PHP, Java, TypeScript, SQL Server, DevOps, CSS, and Android; key curriculum-only content includes general-education subjects (philosophy, history, foreign languages) and theoretical mathematics with limited direct market relevance.

The thesis contributes: a reusable methodology for curriculum–labor market alignment analysis in multilingual, data-scarce contexts; the first structured IT curriculum dataset for Armenian higher education; and an evidence base for targeted curriculum reform in a rapidly growing IT sector that has not previously been studied at this scale or precision.

---

**Keywords:** curriculum alignment, skill gap analysis, NLP, TF-IDF, KeyBERT, ESCO, Armenian IT education, labor market, skill extraction

---

*Supervisor: [supervisor name]*
*Program: [program name]*
*Institution: [institution]*
*Year: 2026*
# Chapter 1: Introduction

## 1.1 Background and Motivation

The Information Technology (IT) sector in Armenia has expanded rapidly over the past decade, becoming a cornerstone of the national economy. This growth—fueled by rising international investment and the emergence of vibrant local tech clusters—has created a constant demand for highly skilled professionals. However, as the industry moves toward complex fields like Data Engineering, Machine Learning, and Cloud Computing, the availability of industry-ready graduates has become a critical bottleneck for further progress [1].

While Armenian universities offer structured academic programs grounded in computer science and applied mathematics, there is a persistent disconnect between formal instruction and the technical competencies employers require. Research by Kupets [2] shows that approximately 30% of urban workers in Armenia are overeducated for their current roles, yet 69.9% of these workers feel their formal education has limited practical use. This structural pattern, rooted in post-Soviet educational path dependency, results in a costly paradox: a skill gap that delays graduate entry into the workforce and stifles growth in a sector that reports thousands of unfilled vacancies despite high graduate numbers [2]. Understanding this gap through quantitative, reproducible evidence is the first step toward improving educational outcomes and ensuring graduates are truly equipped for a rapidly evolving labor market.

## 1.2 Problem Statement

At the heart of this research is the lack of structured, data-driven analysis regarding the alignment between IT higher education and the labor market in Armenia. Currently, most discussions of the "skill gap" rely on qualitative surveys or anecdotal employer feedback rather than systematic, objective measurement [3]. Without a detailed comparison of actual course content against real-world job specifications, it is nearly impossible to identify exactly which competencies are missing from curricula or which courses have lost their market relevance. This study addresses this information deficit by performing a large-scale, automated analysis of university curriculum data and job market postings to identify areas of divergence and alignment with empirical precision.

## 1.3 Research Objectives

The primary goal of this thesis is to provide a quantitative assessment of how well Armenian university IT curricula match the current demands of the domestic job market. To achieve this, the following objectives have been established:

1. To build a structured curriculum dataset by collecting and processing data from 25 programs across four major Armenian universities: Yerevan State University (YSU), the American University of Armenia (AUA), the National University of Architecture and Construction of Armenia (NUACA), and the Russian-Armenian University (RAU).
2. To aggregate a comprehensive job market dataset from 14 diverse sources, including job aggregators (LinkedIn, Staff.am, job.am) and direct company career portals (EPAM, SoftConstruct, Grid Dynamics, NVIDIA, 10Web, Picsart, Krisp, and others), covering a 1,369-posting Armenian market snapshot and a downstream IT-only subset of 753 postings active in March 2026.
3. To implement a Natural Language Processing (NLP) pipeline for automated skill extraction from 1,161 curriculum records and the 753-posting IT-only job-market subset, handling multilingual content (Armenian, English, and Russian).
4. To define and compute alignment metrics — including skill coverage rate, gap sets, and surplus sets — that objectively measure the overlap between educational content and industry demand.

## 1.4 Research Questions

To guide this investigation, the research addresses the following questions:

- **RQ1:** What are the most frequently demanded technical skills in the Armenian IT job market, and how are they distributed across employer types and seniority levels?
- **RQ2:** Which core competencies and technologies are most prevalent in current Armenian university IT curricula, and how do they vary across institutions and programs?
- **RQ3:** To what extent do Armenian IT curricula align with the skill requirements identified in the labor market, and what is the magnitude of the gap?
- **RQ4:** Which specific programs or institutions demonstrate the strongest and weakest alignment with industry demand?

## 1.5 Contribution of the Thesis

This thesis makes the following contributions to the field:

1. **First computational alignment study for Armenian IT education.** To the best of the author's knowledge, this is the first study to apply automated skill extraction and taxonomy-based alignment analysis to Armenian university curricula and job market data jointly.

2. **Multi-source job dataset.** By aggregating a 1,369-posting market snapshot from 14 distinct sources, then deriving a focused 753-posting IT-only analysis subset, this research provides a more representative picture of the Armenian IT labor market than any single-source approach.

3. **Multilingual NLP pipeline.** The methodology is designed to address the challenge of Armenian-language curriculum data (691 of 1,161 course records) alongside English and Russian sources, providing a replicable model for curriculum alignment research in other non-English educational contexts.

4. **Evidence base for curriculum reform.** The study delivers program-level alignment scores and a ranked list of in-demand skills currently absent from curricula. These results provide concrete, actionable inputs for university committees and national accreditation bodies like ANQA.

This work builds on the methodological precedent of Almaleh et al. [4], who applied a similar computational framework in the Saudi Arabian context, and extends it to a unique geographic and linguistic setting.

## 1.6 Scope and Limitations

The analysis covers four Armenian universities for which structured, publicly accessible curriculum data was available at the time of collection (March 2026): YSU, AUA, NUACA, and RAU. The National Polytechnic University of Armenia (NPUA)—one of the country’s largest technical universities with approximately ten IT-related programs—could not be included because its official website blocks automated data access through Cloudflare protections. The Université Française en Arménie (UFAR) was identified but not assessed within the scope of this project. At RAU, data collection was limited to one bachelor-level program. While these exclusions affect the overall representativeness of the curriculum side of the analysis, they are acknowledged as limitations and discussed in detail in Chapter 4.

The job market dataset represents a cross-sectional snapshot of postings active in Armenia in March 2026 and thus does not capture long-term trends in skill demand.

## 1.7 Structure of the Thesis

The remainder of this thesis is organized as follows. Chapter 2 reviews current literature on curriculum–labor market alignment, NLP-based skill extraction, and the specific Armenian educational context. Chapter 3 outlines the theoretical framework, grounding the analysis in constructive alignment theory [5] and using ESCO as the operational layer for skill measurement. Chapter 4 provides a detailed description of the data collection methodology, dataset characteristics, and the NLP analysis pipeline. Chapter 5 presents the empirical findings, including alignment metrics, per-university results, and the identified skill gap. Chapter 6 discusses these findings in relation to the initial research questions and existing literature. Finally, Chapter 7 concludes with a summary of contributions, practical recommendations, and directions for future research.

---

**Chapter references:** [1] World Economic Forum (2025) · [2] Kupets (2016) · [3] Aljohani et al. (2022) · [4] Almaleh et al. (2019) · [5] Biggs & Tang (2011)
# Chapter 2: Literature Review

## 2.1 The Curriculum–Labor Market Gap: An Established Problem

The mismatch between what universities teach and what employers need is not a new observation. It has been documented across regions and disciplines for decades, and it takes two analytically distinct forms. The first is *overeducation*: workers hold credentials that exceed the formal requirements of their positions. The second is *skill mismatch*: workers lack specific technical or practical competencies despite holding formally relevant degrees. Both can coexist, and in post-Soviet transition economies they frequently do [2].

The scale of the problem has attracted growing research attention. Aljohani et al. [3] conducted a systematic review of 10,214 Scopus-indexed records published between 2010 and 2021 on curriculum–labor market alignment, finding a marked increase in publication volume after 2015, driven primarily by the availability of large-scale job posting datasets and advances in natural language processing. Their review identifies three dominant methodological clusters in the field: survey-based employer feedback studies, competency framework mapping exercises, and, most recently, computational corpus analysis studies. The present thesis belongs to the third cluster, which the authors identify as the fastest-growing and methodologically most rigorous approach.

A consistent finding across all three clusters is that the gap is not uniformly distributed. Certain skill categories — particularly those at the intersection of applied computing, data analysis, and communication — appear persistently under-represented in curricula relative to their labor market demand. At the same time, curricula in countries with centralized or historically rigid degree structures tend to carry a surplus of theoretical content that has limited direct employer relevance [2, 6].

---

## 2.2 Computational Approaches to Curriculum Alignment

The shift toward computational methods for curriculum alignment analysis was made possible by two parallel developments: the digitization of university course catalogs and the mass availability of structured job posting data from platforms such as LinkedIn and national job boards. These developments enabled researchers to treat curricula and job advertisements as comparable text corpora and apply information retrieval and NLP techniques to quantify alignment at scale.

The most methodologically proximate study to the present thesis is Almaleh et al. [4], who propose a framework — which they term "Align My Curriculum" — for comparing university course syllabi against job postings from a Saudi Arabian employment portal. Their pipeline combines Naive Bayes text classification with cosine similarity scoring to produce per-course alignment scores and an aggregate institution-level alignment index. Applying this to computing faculties in Saudi Arabia, they find alignment rates below 50% for several programs, with particular deficits in software engineering and data management skills. This study establishes the two-dataset comparative design — one curriculum corpus, one job market corpus — that the present thesis adopts and extends.

The key extensions in the present thesis relative to Almaleh et al. [4] are threefold. First, the job market dataset here spans a 14-source market snapshot combining aggregators and direct employer portals, whereas Almaleh et al. draw from a single portal. Second, the present study handles multilingual input data — Armenian, English, and Russian — while Almaleh et al. operate entirely in English. Third, the skill normalization step here uses the ESCO taxonomy, providing a standardized, internationally recognized vocabulary for reporting gap findings.

A parallel line of work was presented at the 15th International Conference on Educational Data Mining (EDM 2022). Ahadi et al. [7] apply skills analytics to both curriculum documents and job postings to identify skill gaps in a directly comparable framing to the present thesis.

More recently, Musazade et al. [8] introduce the UniSkill dataset, which links university course descriptions to ESCO skills for Systems Analyst and Management Analyst occupations, providing a benchmark for curriculum-to-taxonomy matching. While the occupational scope of UniSkill differs from the present study, its methodology — mapping curriculum text to ESCO concepts via embedding similarity — validates the core approach used here.

---

## 2.3 NLP Methods for Skill Extraction

Extracting skills from unstructured text is a non-trivial NLP task. Job descriptions and course names are typically short, domain-specific, and written in varied stylistic registers. Two broad paradigms exist for this task: unsupervised keyword extraction and supervised sequence labeling.

In the unsupervised paradigm, methods such as TF-IDF and RAKE identify candidate skill phrases based on statistical salience within a document corpus. A more powerful approach in this category is KeyBERT [9], which uses BERT-based sentence embeddings to identify the candidate phrases most semantically similar to the document as a whole. KeyBERT requires no labeled training data, is applicable to short texts, and supports multilingual models — making it well-suited to the curriculum data in this study, where course descriptions are often one or two sentences in length.

The supervised paradigm treats skill extraction as a named entity recognition (NER) problem: a model is trained to label spans of text as skill entities or non-entities. Zhang et al. [10] introduce SkillSpan, a dataset of 14,759 annotated sentences from job postings, and fine-tune transformer-based models on it to produce a state-of-the-art skill extraction system. SkillSpan achieves substantially higher precision on English job posting data than unsupervised alternatives, at the cost of being language- and domain-specific.

For the present thesis, two unsupervised approaches are implemented and compared: TF-IDF keyword extraction and KeyBERT. KeyBERT uses the `all-MiniLM-L6-v2` sentence transformer [12] applied to both curriculum records and job postings, given its suitability for short texts and computational efficiency for large-scale corpus processing. All curriculum text is available in English after translation (Section 4.4), making an English-only model sufficient. The sentence embedding architecture underlying KeyBERT builds on Reimers and Gurevych [11], which produces fixed-length sentence representations optimized for semantic similarity tasks. SkillSpan [10] represents the state-of-the-art in supervised skill extraction and is cited here as the benchmark that unsupervised methods are measured against in the literature, but its use requires labeled training data that was not available for Armenian curriculum texts and therefore falls outside the scope of this study.

A persistent challenge in skill extraction is the distinction between a *skill* (a competence a person can possess) and a *topic* or *requirement* mentioned in context. A job posting that mentions "microservices architecture" may be describing a system the candidate will work with rather than a skill they must possess. This ambiguity is inherent to the task and cannot be fully resolved by automated methods alone. The methodology section (Chapter 4) documents the quality validation steps taken to assess and partially address this issue.

---

## 2.4 Skill Taxonomies as Measurement Frameworks

Extracted skill phrases, in their raw form, are not directly comparable across sources: a job posting may demand "Python scripting," a course may teach "programming in Python," and a taxonomy may list "Python (programming language)" — these are semantically equivalent but textually distinct. A shared taxonomy is therefore necessary to normalize extracted phrases to a common vocabulary before any alignment comparison can be made.

Three taxonomies are relevant to this study: ESCO, O*NET, and SFIA.

**ESCO** (European Skills, Competences, Qualifications and Occupations) is a multilingual taxonomy developed by the European Commission. It currently comprises 3,039 occupation concepts and 13,939 skill and competence concepts, organized in 28 languages [14]. ESCO was explicitly designed to serve as an interface between the education and employment systems — its conceptual architecture links occupations to the skills they require and qualifications that support entry into them. This design philosophy makes ESCO the most appropriate primary taxonomy for a study that bridges curricula and job market data. Furthermore, Armenian universities operate within the Bologna Process framework, which is the European higher education architecture that ESCO was built to complement.

ESCO has known limitations. Chiarello et al. [15] demonstrate that ESCO coverage of Industry 4.0 skills — including IoT, AI applications, and robotics — lags significantly behind actual industry practice, due to the taxonomy's update cycle. For the present study, this means that recent or niche skills found in job postings from cutting-edge companies (such as prompt engineering, LangChain, or specific cloud service APIs) will not match any ESCO concept. Rather than treating this as a failure of the methodology, these unmatched terms are retained as a separate "emerging skills" category, which itself constitutes a finding: they represent the fastest-moving frontier of IT skill demand that formal taxonomies have not yet absorbed.

**O*NET** (Occupational Information Network) is the U.S. Department of Labor's occupational taxonomy, providing structured descriptors for approximately 1,000 occupations. While O*NET's occupational detail exceeds ESCO's in some areas, its U.S.-centric framing and lack of multilingual support make it less appropriate as the primary taxonomy for an Armenian study. It is referenced here as a secondary cross-validation tool: where findings map to identifiable O*NET skill categories, this is noted to improve accessibility for international readers.

**SFIA** (Skills Framework for the Information Age) is an IT-specific professional skills framework that organizes 121 technical and managerial skills across seven levels of responsibility [16]. Unlike ESCO and O*NET, SFIA is designed exclusively for the IT profession. While it does not provide an accessible API or downloadable dataset that supports programmatic matching at scale, its seven-level responsibility structure — ranging from "Follow" (level 1) to "Set strategy" (level 7) — is used in the discussion chapter to characterize the *type* of skill gap identified: whether universities are teaching the right skills at the wrong level, or missing skill categories entirely.

---

## 2.5 The Armenian and Post-Soviet Educational Context

Understanding the nature of any curriculum–labor market gap in Armenia requires engagement with the structural conditions of Armenian higher education, which cannot be read off from comparative studies conducted in Western European or North American contexts.

Armenia's higher education system is a product of the Soviet institutional architecture: centralized degree structures, strong theoretical emphasis, weak differentiation between research and teaching functions, and limited responsiveness to labor market signals [2]. Following independence in 1991, Armenia underwent a series of reform attempts, including formal accession to the Bologna Process in 2005. Bologna adoption introduced the two-cycle degree structure (Bachelor/Master), European Credit Transfer System (ECTS) compatibility, and a formal commitment to learning-outcome-based curriculum design. However, adoption has been uneven: the degree structure has largely been implemented, but outcome-based curriculum design and employer-facing program review remain less consistently embedded in practice [2].

Kupets [2] provides the most directly relevant empirical evidence for the Armenian context, drawing on World Bank STEP household survey data. Key findings include: approximately 30% of urban Armenian workers are overeducated for their positions; 69.9% of overeducated workers report their formal education has limited practical usefulness; and the IT sector specifically reports thousands of unfilled vacancies despite high numbers of computing graduates. Kupets frames this as a structural mismatch — not a failure of individual graduates — rooted in the Soviet-era curriculum's emphasis on abstract theoretical knowledge over applied technical competence. This framing directly motivates the present study: if the gap is structural, it can only be diagnosed and addressed through structural data, not through individual graduate surveys.

The Armenian IT sector has expanded substantially since the period studied by Kupets [2]. Major international companies have established development centers in Yerevan (EPAM, SoftConstruct, ServiceTitan), domestic technology companies have scaled internationally (Picsart, Krisp), and diaspora investment has seeded a range of startups and accelerators. This expansion has increased both the volume and the specificity of employer skill demands in the local market, potentially widening the curriculum gap documented in earlier survey research. The present thesis provides a contemporaneous, data-driven update to that earlier evidence base.

The closest regional academic comparator is Amirova and Valiyev [6], who study the competence gap in Azerbaijan — a former Soviet republic with close structural and cultural similarity to Armenia in its higher education system. Their survey-based study of 24 competences finds sharp disagreement between employers and graduates on which competences are most important: employers prioritize practical technical skills and communication, while graduates overestimate the value of formal theoretical credentials. This pattern is consistent with the structural account offered by Kupets [2] and provides a qualitative benchmark against which to interpret the quantitative findings of the present study.

---

## 2.6 Constructive Alignment and the Theoretical Case for Measurement

The concern with curriculum–labor market alignment has a well-developed theoretical base in educational research. Biggs and Tang [5] introduce the concept of *constructive alignment* — the principle that effective teaching requires internal coherence between three elements: intended learning outcomes (ILOs), teaching and learning activities, and assessment tasks. A curriculum in which assessments do not test what the ILOs specify, or in which teaching activities do not lead students toward the stated outcomes, is structurally misaligned even before any external labor market comparison is made.

Biggs and Tang developed constructive alignment primarily as a framework for internal curriculum quality. However, the same logic extends naturally to external alignment: if ILOs are to be educationally meaningful, they should reflect competences that graduates will actually use in professional life. When a systematic gap exists between what a curriculum declares it teaches and what employers need graduates to know, the external misalignment is often a symptom of an earlier failure to define ILOs with reference to any external standard.

In the context of Armenian universities, this connection is particularly relevant. As noted above, outcome-based curriculum design has been formally adopted as part of Bologna compliance, but implementation is uneven. For several universities in this study — notably YSU, whose course data provides names but limited or no description fields — the absence of published ILOs means that skill content must be inferred entirely from course names. This is a methodological constraint, but also a diagnostic signal: programs whose curricula cannot be analyzed because learning outcomes are not documented are the same programs most likely to be misaligned with labor market expectations.

The operationalization of "skills" in this thesis follows the task-based framework introduced by Autor, Levy, and Murnane [13]. In their model, occupations are characterized by the tasks they require — cognitive or manual, routine or non-routine — and the value of skills is defined by which tasks they enable. This framework underpins the use of job posting text as a proxy for skill demand: a job description specifies the tasks an employer needs performed, and the skills listed or implied in that description are those that enable task completion. ESCO, as the normalization target for extracted skills, encodes this task-skill relationship: each ESCO skill concept is linked to the occupations whose tasks it supports.

---

## 2.7 Summary and Research Gap

The literature reviewed in this chapter establishes three points that motivate the present thesis. First, curriculum–labor market misalignment is a documented and consequential problem, particularly in post-Soviet transition economies where structural path dependency limits curriculum responsiveness to changing employer demand. Second, computational alignment analysis using NLP and skill taxonomies is an established and growing methodology with several published precedents, the most closely related being Almaleh et al. (2019). Third, no prior study has applied this methodology to the Armenian context, and the existing evidence base for Armenia relies on survey-based data that is now a decade old.

This thesis fills that gap by constructing the first large-scale, multi-source, computationally analyzed curriculum–job market alignment dataset for Armenian IT higher education, and by applying a reproducible NLP pipeline to quantify the skill gap at program and institution level.

---

**Chapter references:** [2] Kupets (2016) · [3] Aljohani et al. (2022) · [4] Almaleh et al. (2019) · [5] Biggs & Tang (2011) · [6] Amirova & Valiyev (2021) · [7] Ahadi et al. (2022) · [8] Musazade et al. (2026) · [9] Grootendorst (2020) · [10] Zhang et al. (2022) · [11] Reimers & Gurevych (2019) · [12] Wang et al. (2020) · [13] Autor et al. (2003) · [14] European Commission (2023) · [15] Chiarello et al. (2021) · [16] SFIA Foundation (2021)
- *Grootendorst, M. (2020) — KeyBERT, Zenodo software release, DOI: 10.5281/zenodo.4461265 — verified ✓ (cite as @misc Zenodo, not journal)*
- *Zhang et al. (2022) — SkillSpan, NAACL, verified ✓*
- *Reimers & Gurevych (2019) — Sentence-BERT, EMNLP, verified ✓*
- *European Commission (2023) — ESCO documentation — add URL in references*
- *Chiarello et al. (2021) — Technological Forecasting and Social Change, verified ✓*
- *SFIA Foundation (2021) — sfia-online.org — add URL in references*
- *Amirova & Valiyev (2021) — Journal of Teaching and Learning for Graduate Employability, verified ✓*
- *Biggs & Tang (2011) — Teaching for Quality Learning, verified ✓*
- *Autor, Levy & Murnane (2003) — Quarterly Journal of Economics, verified ✓*
# Chapter 3: Theoretical Framework

## 3.1 Overview

This chapter presents the theoretical foundations that underpin the research design, analytical choices, and interpretive lens of this thesis. Three interconnected frameworks are employed. Constructive alignment theory [5] provides the educational rationale for why curriculum–labor market alignment matters and what a properly aligned curriculum would look like. The task-based view of skill demand [13] provides the labor economics rationale for treating job postings as a valid proxy for skill demand. ESCO [14] serves as the operational bridge between the two: a shared vocabulary that makes it possible to compare what curricula teach against what employers need using a single, standardized measurement instrument.

Together, these three frameworks justify the central methodological claim of this thesis: that the distance between what is taught in Armenian IT programs and what employers demand can be measured, quantified, and disaggregated at the level of individual programs and institutions.

---

## 3.2 Constructive Alignment [5]

Section 2.6 introduced constructive alignment and established its external dimension: a curriculum that is internally coherent (ILOs, TLAs, and ATs mutually reinforcing) but externally disconnected from labor market requirements will produce graduates who perform well on assessments but are not equipped for employment — the pattern Kupets [2] documents empirically for Armenia. This section describes how that theoretical argument is operationalized in the present study.

The operationalization proceeds in two steps. First, curriculum documents are treated as ILO proxies: where course descriptions or published program learning outcomes are available, they serve directly as evidence of what a course intends students to learn. Where they are absent — as is the case for the majority of YSU courses, which provide course names only — the course name itself is used as the best available approximation of the intended learning target. Second, job postings are treated as proxies for the external reference standard against which ILOs should be evaluated: the task requirements and competences that Armenian IT employers actually need graduates to possess. The gap between the skills inferable from these ILO proxies and the skills demanded in job postings is the central measurement object of the study.

This operationalization has a methodological implication worth stating explicitly: programs with richer published learning outcome documentation (particularly AUA, which provides full course descriptions) will yield more nuanced skill profiles than programs with minimal documentation (particularly YSU). This asymmetry is not a flaw in the data — it reflects a real difference in curriculum transparency between institutions. It is also, from a constructive alignment perspective, a finding in itself: a program whose intended learning outcomes are not published cannot be evaluated for external alignment, which is the same opacity that prevents employer-facing program review. The asymmetry is discussed as a limitation in Chapters 4 and 6.

Within the post-Soviet institutional context, constructive alignment failure takes a specific form. The inherited curriculum architecture emphasized theoretical depth and formal derivations — competences that could be internally assessed through written examinations — rather than the applied, task-oriented competences that external alignment with an IT labor market would require. This structural inheritance is the mechanism through which the misalignment documented in this thesis is expected to have accumulated: not through individual pedagogical failures, but through a system-level ILO design that never took the labor market as its reference point.

---

## 3.3 Task-Based View of Skill Demand [13]

The labor economics literature offers a complementary theoretical account of why skill taxonomies are an appropriate instrument for measuring labor market demand. Autor, Levy, and Murnane [13] propose that occupations are most usefully characterized not by their titles or credential requirements, but by the *tasks* they require workers to perform. In their framework, tasks are classified along two dimensions: cognitive versus manual, and routine versus non-routine. The key insight is that technology substitutes most readily for routine tasks (both cognitive and manual) and complements non-routine cognitive tasks — a pattern that drives the growing premium on higher-order analytical, communicative, and adaptive skills in knowledge-intensive labor markets.

This framework has three implications for the present thesis.

First, it provides the theoretical justification for using job postings as a source of skill demand data. A job posting is, at its core, a specification of the tasks an employer needs a hire to perform and the skills those tasks require. The skills listed or implied in a job description — programming languages, analytical methods, domain knowledge, soft competencies — are a direct expression of task requirements in the Autor et al. sense.

Second, it suggests that skill taxonomies (ESCO, O*NET) are not arbitrary classification systems but attempts to systematically encode the task-skill structure of occupations. ESCO's organization of skills into knowledge, skills (procedural), and attitudes mirrors the cognitive/behavioral task decomposition of the Autor et al. framework. Using ESCO as the normalization target is therefore not merely a practical convenience but a theoretically grounded choice.

Third, the task-based framework predicts the direction of the gap that this thesis is likely to find: post-Soviet curricula, which were designed under different technological and economic conditions, are expected to over-represent routine cognitive content (memorization, formal derivations, algorithmic procedures) relative to the non-routine cognitive and communicative skills that contemporary IT employers value most. Whether this prediction is confirmed by the data is an empirical question answered in Chapter 5.

---

## 3.4 ESCO as the Operational Bridge

ESCO (European Skills, Competences, Qualifications and Occupations) is the operational instrument that makes it possible to compare curricula and job postings on a shared basis. Its role in the theoretical framework is distinct from its role in the methodology: theoretically, ESCO represents the commitment to a standardized, intersubjective definition of "skill" — a definition not constructed by this thesis but established by the European Commission through an iterative, multi-stakeholder process [14].

The choice of ESCO over alternative taxonomies (O*NET, custom domain dictionaries) is grounded in three theoretical considerations. First, ESCO was explicitly designed for the education–employment interface: its conceptual architecture links skill concepts to the occupations that require them and to the qualifications that signal their acquisition. This tripartite structure makes it uniquely appropriate for a study that spans both educational institutions and employer organizations. Second, ESCO's multilingual coverage — available in 28 languages — is necessary for handling the linguistically diverse inputs of this study (Armenian, English, Russian). Third, Armenia's integration into the Bologna Process means that the European higher education framework, of which ESCO is the skills component, represents the normative reference standard against which Armenian curricula are being designed and evaluated.

One theoretical tension requires acknowledgment. ESCO is a static snapshot that is updated on a fixed release cycle, meaning it necessarily lags behind the fastest-moving areas of technology practice. The task-based framework of Autor et al. [13] implies that new task types — those created by emerging technologies — will generate new skill demands before any formal taxonomy can absorb them. In this study, skill phrases extracted from job postings that do not match any ESCO concept are treated as empirical evidence of this theoretical expectation: they are the labor market's leading edge, visible in practice before it is visible in formal classification systems.

---

## 3.5 Integration of the Three Frameworks

The three frameworks converge on a single analytical structure illustrated in Figure 3.1.

> **[Figure 3.1 — Integrated Theoretical Framework]** *Insert clean flowchart here. Replace the diagram below with the exported PNG. See `docs/thesis/FIGURE_PLACEMENT_GUIDE.md`.*

```
CONSTRUCTIVE ALIGNMENT (Biggs & Tang)
  ↓
  Curriculum ILOs  ←——→  are they aligned with  ←——→  Labor market task requirements
  (course names,                                        (job postings)
   descriptions,
   learning outcomes)
            ↓                                                    ↓
        [ESCO normalization — shared skill vocabulary]
            ↓                                                    ↓
     Curriculum skill profile                       Job market skill profile
            ↓                                                    ↓
                    [Gap analysis — coverage rate, gap set, surplus set]
                                        ↓
                    Findings interpreted through:
                    - Constructive alignment: what does the gap mean for ILO quality?
                    - Task-based view: are gap skills routine or non-routine cognitive?
                    - SFIA levels: is the gap about missing skills or wrong skill depth?
```
*Figure 3.1. Integrated analytical framework combining constructive alignment theory, task-based skill demand, and ESCO normalization.*

This integrated structure means that the thesis is not merely reporting a gap — it is interpreting the gap through three complementary lenses. The constructive alignment lens asks: *is the gap a sign of weak ILO design?* The task-based lens asks: *is it a sign of technological change outpacing curriculum response?* The ESCO lens makes the gap measurable, reproducible, and comparable with other studies.

---

## 3.6 Summary

The theoretical framework of this thesis is built on three mutually reinforcing foundations. Constructive alignment theory provides the educational logic for why the curriculum–labor market gap is a structural, not individual, problem — and why it can only be diagnosed by examining ILOs against external standards. The task-based framework of labor economics provides the theoretical basis for treating job postings as valid proxies for skill demand, and for expecting the gap to concentrate in non-routine cognitive and communicative skills. ESCO provides the operational instrument that translates both curriculum content and job market requirements into a shared, internationally standardized vocabulary, enabling objective and reproducible comparison.

Taken together, these frameworks position this thesis as a study that is simultaneously grounded in educational theory, informed by labor economics, and implemented through applied NLP — three disciplines that must work together to address the curriculum alignment problem rigorously.

---

**Chapter references:** [2] Kupets (2016) · [5] Biggs & Tang (2011) · [13] Autor et al. (2003) · [14] European Commission (2023) · [16] SFIA Foundation (2021)
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
# Chapter 6: Discussion

---

## 6.1 Overview

This chapter interprets the empirical findings reported in Chapter 5 through the three theoretical lenses introduced in Chapter 3: constructive alignment [5], the task-based view of skill demand [13], and ESCO as an operational bridge [14]. It then situates the results in the context of the existing literature reviewed in Chapter 2 and directly addresses each of the four research questions. Section 6.4 discusses methodological contributions and limitations. Section 6.5 draws implications for policy and practice.

---

## 6.2 Interpreting the Findings Through the Theoretical Frameworks

### 6.2.1 Constructive Alignment Lens: What Does the Gap Mean for ILO Quality?

The constructive alignment framework [5] predicts that a curriculum is externally misaligned when its intended learning outcomes (ILOs) are not defined with reference to external standards — in this case, the skill demands of the Armenian IT labor market. The findings in Chapter 5 are consistent with this prediction.

The surplus content identified in the analysis — philosophy, history, physical education, Armenian language — reflects a state educational standard inherited from the Soviet-era centralized curriculum architecture, not program-level pedagogical decisions. These courses serve a different educational function (civic education, cultural formation) and cannot be evaluated for labor market alignment. Their presence in the surplus is a structural feature of the Armenian degree framework, not a critique of individual program design.

The more diagnostically significant surplus consists of theoretical STEM content: differential equations, linear algebra, Monte Carlo simulation, biostatistics, MATLAB, and Assembly programming. These courses could plausibly serve as foundations for applied technical skills (mathematical optimization for machine learning, numerical methods for simulation), but this connection is not visible from course names or job posting text alone. Whether these courses build competences that employers value requires a learning-outcome-level analysis beyond the scope of the present study. They appear in the surplus because their ILOs — where published — describe theoretical mastery rather than applied competence, and employers do not name foundational subjects in job postings.

The gap content — Docker, Kubernetes, CI/CD, DevOps, cloud infrastructure, REST APIs, microservices — represents a qualitatively different alignment failure. These are not emergent technologies: Docker was released in 2013, Kubernetes in 2014, and DevOps as a discipline predates both. Their complete absence from Armenian IT curricula in 2026 is a lagging indicator of a curriculum update cycle that has not kept pace with professional practice for more than a decade. From a constructive alignment perspective, this indicates that the ILOs of software engineering and systems programs have not been reviewed against current labor market requirements for a significant period. This is the most actionable finding of the study.

### 6.2.2 Task-Based Lens: Routine vs. Non-Routine Cognitive Skills

The task-based framework of Autor, Levy, and Murnane [13] classifies job tasks along the cognitive–manual and routine–non-routine axes. It predicts that labor market demand concentrates on non-routine cognitive tasks — analysis, synthesis, adaptive problem-solving — as automation substitutes for routine cognitive tasks.

The gap skills identified in this study align with this prediction. Containerization (Docker, Kubernetes), infrastructure-as-code (Terraform), CI/CD pipeline management, and cloud deployment are non-routine cognitive tasks: they require adaptive reasoning about complex distributed systems, debugging across multiple abstraction layers, and continuous integration of rapidly evolving tooling ecosystems. The fact that these skills are simultaneously the most in demand and the most absent from curricula is consistent with the task-based framework's implication that educational systems systematically underinvest in the non-routine competences that provide the highest wage premium in the current labor market.

The surplus content, by contrast — calculus, differential equations, linear algebra, formal logic — is associated with routine cognitive task patterns: formal derivations following well-defined procedures. This does not make them valueless (they develop abstract reasoning capacity that underlies applied competences), but it explains why they are not directly requested in job postings. Employers purchase the outputs of foundational training without explicitly naming the courses that produced them.

The knowledge/competence split in the ESCO overlap reinforces this interpretation. Of the 107 overlapping ESCO concepts (TF-IDF), 77.6% are classified as *knowledge* and 22.4% as *skill/competence*. The gap is approximately balanced (48.9% knowledge, 51.1% applied competence). Armenian curricula are stronger on the knowledge transmission side of the task spectrum and weaker on applied competence — precisely where the task-based framework predicts the largest market premium.

### 6.2.3 ESCO Lens: Structural Coverage and Emerging Skills

The ESCO-normalized results reveal two analytically distinct layers of the alignment picture.

The first layer is **structural coverage within the ESCO vocabulary**. Armenian IT curricula cover 332 unique ESCO concepts (TF-IDF) against a job market demand of 326 — a 32.82% overlap. This means that roughly two thirds of employer-demanded ESCO concepts still have no representation in any Armenian IT curriculum. The gap is not concentrated in exotic or niche areas: it includes PHP, Java, TypeScript, SQL Server, DevOps, and CSS — mainstream technologies and practices taught in the majority of contemporary software engineering programs.

The second layer is **emerging skills beyond ESCO**. The supplementary tech lexicon analysis identified 25 specific modern tools absent from or poorly represented in ESCO v1.2. Azure (35 postings), React (30), AWS (20), Google Cloud (8), Kubernetes (6), Docker (5), and Terraform (5) all have zero curriculum presence. LLM/GenAI tools (25 postings) and Node.js (20) are the only major emerging categories with any curriculum representation (4 and 3 courses respectively), suggesting limited early adoption. The absence of cloud platforms, containerization, and infrastructure-as-code from curricula while these tools appear repeatedly in employer demand represents the most concrete and time-sensitive curriculum reform target.

### 6.2.4 Synthesis: A Coherent Picture Across Three Lenses

All three frameworks converge on the same diagnosis. Constructive alignment identifies the absence of ILO review against labor market standards. The task-based framework identifies a systematic underinvestment in non-routine applied competences. ESCO normalization quantifies the gap as concentrated in applied tool-level skills that have been in stable market demand for over a decade.

The structural pattern that emerges is: Armenian IT curricula are well-aligned with the *knowledge* layer of the job market (shared subject domains — algorithms, data structures, programming foundations, databases) but systematically lag in the *applied competence* layer (specific tools, workflows, and deployment practices). This gap is not random or idiosyncratic — it follows the boundary between formal academic content and professional practice. It is a gap that structured industry engagement, capstone projects, and curriculum co-design with employers could plausibly close.

---

## 6.3 Addressing the Research Questions

### RQ1: Most frequently demanded skills in the Armenian IT job market

The most frequently demanded skills in the Armenian IT job market, as identified by the direct frequency analysis on the IT-only market subset, cluster into four categories:

1. **Programming languages and platforms:** Python, Java, .NET / C#, TypeScript, Node.js, React
2. **Modern software delivery tools:** CI/CD, Docker, Kubernetes, DevOps, Terraform
3. **Cloud and infrastructure:** AWS, Azure, Google Cloud, microservices, REST APIs
4. **Core competences:** testing, software design, Agile, project management methodologies

The source composition of the dataset shapes this demand signal. LinkedIn contributes 556 of the 753 IT-only postings and therefore skews the market view toward roles posted by larger, more formal employers. SoftConstruct contributes 37 IT-only postings and still introduces some gaming and betting industry vocabulary — notably, ESCO concepts such as *betting* and *banking activities* remain visible in the raw gap list. These domain-specific demands are reported in full but should be understood as employer-specific rather than sector-wide IT requirements. They do not change the main IT-specific gap story, which is centered on PHP, Java, TypeScript, DevOps, SQL Server, responsive design, CSS, and Android-related practice.

### RQ2: Most prevalent competences in Armenian IT curricula

The most prevalent skills in Armenian IT curricula reflect the composition of the university sample. YSU, contributing 59.5% of courses, dominates the curriculum vocabulary. Frequent curriculum concepts include: algorithms, computer science foundations, data structures, programming (Python, C++, Java), databases, mathematical analysis, networks, and software engineering fundamentals.

AUA shows the highest density of applied technical content per course, consistent with its American-model pedagogy and fully available course descriptions. YSU has broader theoretical coverage but lower applied technology density per course. The overlap in extracted ESCO concepts between AUA and YSU reflects genuine pedagogical similarity in foundational content, despite their different institutional models.

NUACA and RAU, with name-only course records, yield the most conservative skill profiles. The finding that 48% of NUACA courses and 56% of RAU courses produce zero ESCO concept assignments — compared to 12% for AUA — is primarily a measurement limitation (description asymmetry) rather than a finding about curricular content. However, it is also consistent with programs that are less documentation-transparent and may have less structured learning outcome specification.

### RQ3: Overall alignment magnitude

The pre-ESCO baseline alignment rate is 8.85% (TF-IDF string match) and 0.33% (KeyBERT). These figures substantially underestimate true conceptual alignment due to synonymous phrasing — a phrase pair like "object oriented programming" and "OOP principles" counts as non-overlapping at the string level.

After ESCO normalization, the alignment rises to **32.82%** (TF-IDF) and **28.5%** (KeyBERT). The estimates remain robust across threshold variation: lowering the threshold adds matched phrases but not many new concepts, confirming the bottleneck is ESCO vocabulary coverage rather than calibration sensitivity.

The 32.82% figure means that roughly one in three skills expressible in ESCO v1.2 that employers demand is covered somewhere across Armenian IT curricula. This figure is best interpreted as a lower bound, for two reasons: (1) ESCO v1.2 does not contain many modern tools that are both demanded and potentially taught (Docker, React, Azure), and (2) NUACA and RAU scores are structurally suppressed by name-only description coverage. Adjusting for these factors, the true alignment is likely meaningfully higher — but the present methodology cannot produce a precise adjusted estimate.

### RQ4: Programs with strongest and weakest alignment

The per-program ESCO-normalized results confirm the structural hypotheses:

- **AUA programs lead** (8.06% average coverage). AUA Computer and Information Science (Master) achieves 12.27%, AUA Computer Science (Bachelor) 10.74%, and AUA Data Science (Bachelor) 8.28%. AUA's advantage reflects fuller course descriptions and an applied-technology-oriented curriculum.
- **YSU programs cluster in the middle** (5.96% average). Data Science in Business (7.98%), Information Systems Development (7.98%), and Applied Statistics programs (6.13%–6.75%) lead the YSU group. The more theoretically oriented programs rank lower.
- **NUACA programs occupy the lower range** (2.52% average, with GIS at 0.92%). This reflects both name-only data and a curriculum oriented toward architecture, construction, and geographic information systems rather than software industry practice.
- **RAU's single program** aligns at 2.76%, above the lower NUACA range but below most YSU and AUA programs, consistent with its strong theoretical mathematics orientation.

The wide spread between best (12.27%) and worst (0.92%) program confirms that alignment varies more within institutions than between them. Degree level is not a significant predictor (Bachelor 5.69% vs. Master 5.66%), indicating that graduate programs are not systematically better aligned with market demand than undergraduate ones. This is notable: it suggests that the curriculum gap is not primarily a matter of educational level but of curriculum design priorities.

---

## 6.4 Methodological Contributions and Limitations

### 6.4.1 Methodological Contributions

This study makes three methodological contributions to the curriculum–labor market alignment literature.

**First, a reusable pipeline for multilingual, data-scarce contexts.** The combination of automated scraping, LLM-assisted translation (Armenian → English), two-method unsupervised skill extraction, and ESCO normalization via sentence embeddings produces an end-to-end reproducible pipeline that does not require manually labeled training data. This is particularly relevant for contexts — Central Asian, Eastern European, and South Caucasus higher education systems — where structured curriculum data and labeled skill corpora do not exist.

**Second, LLM-as-annotator for threshold calibration.** Rather than requiring manual annotation of all 293 calibration pairs, GPT-4o-mini was used as an automated judge (temperature=0), following the LLM-as-annotator approach validated in recent NLP research [20, 21]. A 35-pair stratified human spot-check confirmed 94.3% agreement. This calibration approach is time-efficient, reproducible, and achieves comparable annotation quality to full manual annotation for binary match/no-match judgements.

**Third, a two-layer analysis combining ESCO normalization with a supplementary tech lexicon.** ESCO normalization captures conceptual alignment within the formal taxonomy vocabulary; the tech lexicon layer captures the most important emerging tools that ESCO v1.2 does not yet include. Reporting both layers — separately and transparently — provides a more complete picture than ESCO alone, while making the contribution of each layer explicit.

### 6.4.2 Limitations

**Data coverage.** The curriculum side covers four universities. NPUA (approximately ten IT programs, the largest technical university in Armenia) was inaccessible due to Cloudflare bot protection. UFAR was not assessed. These omissions mean findings cannot be generalized to Armenian IT higher education as a whole.

**Temporal snapshot.** All job postings were collected in March 2026. No longitudinal comparison is possible. The job market composition reflects the specific economic and technological conditions of that moment.

**Description asymmetry.** The 5× coverage difference between full-description programs (AUA) and name-only programs (NUACA, RAU) means per-institution comparisons are not structurally equivalent. NUACA and RAU alignment scores are lower bounds. The finding that 48–56% of their courses contribute zero ESCO concepts is partly a data limitation, not purely a curriculum content finding.

**Unsupervised extraction ceiling.** TF-IDF recall against human-curated skill tags is 44%, KeyBERT 21%. Approximately half of identifiable skills are not retrieved. The alignment rates are partial estimates, not upper bounds on true alignment.

**ESCO vocabulary lag.** ESCO v1.2 does not contain Docker, Kubernetes, React, Azure, and other tools in active professional use. The relatively low phrase-to-taxonomy match rate reflects this structural vocabulary gap. The 32.82% coverage figure therefore understates true alignment for the most modern technology layers of both curricula and job postings.

**Single false positive identified.** The phrase `docker` maps to the ESCO concept *dock operations* (maritime logistics) at similarity 0.761 — a known embedding collision. This marginally inflates the job-market gap count by one concept. The impact is negligible but exemplifies the precision risk in similarity-based taxonomy matching.

---

## 6.5 Comparison with Prior Studies

The methodological parallel with Almaleh et al. [4] is direct: both studies apply a two-corpus NLP pipeline to measure curriculum–job market alignment in a developing country higher education context. Both find low baseline overlap rates, consistent with the cross-national finding that curriculum–labor market gaps are structurally common where curriculum design operates without institutionalized employer-facing review. The present study extends this approach with ESCO normalization and a multilingual preprocessing pipeline.

The validation results (44% TF-IDF soft recall against human skill tags) are consistent with skill extraction benchmarks reported by Ahadi et al. [7] for TF-IDF applied to curriculum data in an Australian context. Cross-national consistency in extraction quality suggests the results are not anomalous for this method class.

The UniSkill framework [8] provides the most direct methodological parallel for the ESCO normalization step: curriculum-to-ESCO mapping via embedding similarity, evaluated with calibrated thresholds. The calibrated threshold of 0.75 (F1=0.711) used in this study is consistent with the operating thresholds reported in the UniSkill benchmark, providing an external plausibility check on the calibration approach.

Compared to studies that use supervised skill extraction (SkillSpan [10], ESCOXLM-R), the present approach trades extraction precision for accessibility: labeled training data for Armenian curriculum text does not exist, making supervised approaches inapplicable. The 44% soft recall achieved by TF-IDF is lower than supervised benchmarks but is consistent with the literature on unsupervised curriculum skill extraction and is sufficient for the comparative alignment analysis the study performs.

---

## 6.6 Implications for Policy and Practice

### 6.6.1 For University Curriculum Committees

The most actionable finding is the complete absence of DevOps tooling (Docker, Kubernetes, CI/CD), cloud platforms (AWS, Azure, Google Cloud), and modern web frameworks (React, Node.js) from all 25 programs in the dataset. These are not specialised or company-specific tools; they represent the baseline infrastructure of professional software development practice. The following additions would directly close the largest measured gaps:

- **Software engineering and information systems programs** (all universities): integrate containerization (Docker, Kubernetes), CI/CD fundamentals, and at least one cloud platform (AWS or Azure) into existing DevOps or software deployment modules.
- **Data Science programs** (YSU, AUA): add cloud-based ML deployment and API design to the applied curriculum; LLM/GenAI tools are already present in 4 courses but should be expanded and structured.
- **Computer Science programs** (AUA, YSU): TypeScript, React, and Node.js are demanded across 17–25 job postings and have zero curriculum representation; a modern web development module would close this gap.

AUA's curriculum design and description transparency already reflect better alignment; its approach — structured learning outcomes, full course descriptions, applied technology modules — could serve as a reference model for curriculum review at YSU and NUACA.

### 6.6.2 For National Accreditation Bodies (ANQA)

The description asymmetry finding has a direct policy implication: 48–56% of NUACA and RAU courses are invisible to any automated or systematic alignment analysis because their learning content is not publicly documented beyond a course name. Mandating structured learning outcome publication — even minimal structured descriptions in a standardized format — as part of program accreditation requirements would make future alignment monitoring possible and would incentivize programs to articulate their competence development logic explicitly.

Additionally, the finding that degree level (Bachelor vs. Master) does not predict alignment strength suggests that graduate program accreditation should be evaluated on the basis of applied competence outcomes, not solely on theoretical depth. Programs with strong market demand for the skills they teach are better prepared to justify their resource allocation to accreditors and employers alike.

### 6.6.3 For Students

The gap analysis results function directly as a self-study roadmap for students seeking to improve their market readiness. The skills most frequently demanded in the Armenian IT job market but absent from all curricula in this study — Docker and containerization, Kubernetes, CI/CD and GitLab pipelines, AWS or Azure fundamentals, TypeScript, React, and REST API design — are learnable through documented online pathways. The ranked gap list in Section 5.4.6 provides a prioritized starting point grounded in the observed Armenian market demand.

Students in NUACA and RAU programs, whose institutional alignment scores are most affected by description asymmetry, should note that the low scores reflect measurement limitations more than curriculum content: the actual teaching in those programs likely covers more applied material than name-only course data can detect.

---

**Chapter references:** [4] Almaleh et al. (2019) · [5] Biggs & Tang (2011) · [7] Ahadi et al. (2022) · [8] Musazade et al. (2026) · [10] Zhang et al. (2022) · [13] Autor et al. (2003) · [14] European Commission (2023) · [15] Chiarello et al. (2021) · [20] Gilardi et al. (2023) · [21] He et al. (2024)
# Chapter 7: Conclusion

## 7.1 Summary of the Study

This thesis set out to answer one question: how well do Armenian IT university curricula align with the skill demands of the Armenian IT labor market? To answer it, a five-stage NLP pipeline was constructed, applied to a purpose-built dataset of 1,161 curriculum courses from 25 programs across four universities and a 1,369-posting market snapshot from 14 sources, with a downstream IT-only subset of 753 postings used for NLP and alignment analysis — the first dataset of its kind for the Armenian context.

The pipeline produced two types of results. The first is a pre-ESCO baseline: a raw string-level overlap of 8.85% (TF-IDF) and 0.33% (KeyBERT) between the curriculum and job market skill vocabularies — a lower bound suppressed by synonymous phrasing. After applying a calibrated ESCO similarity threshold of 0.75 (F1=0.711, validated against 293 annotated pairs), coverage rises to 32.82% (TF-IDF) and 28.5% (KeyBERT). The best-performing program — AUA Computer and Information Science (Master) — covers 12.27% of employer-demanded ESCO concepts; the weakest — NUACA Geographic Information Systems (Master) — covers 0.92%.

Regardless of the exact ESCO-normalized figure, the structural findings are clear:

1. **The skill gap is real and concentrated.** Employer-demanded DevOps and cloud infrastructure skills — Docker, Kubernetes, CI/CD, Terraform, cloud platforms — are consistently absent from curriculum text. These are not emerging technologies; they have been in professional use for over a decade. Their absence reflects a structural lag in curriculum update cycles.

2. **The curriculum carries significant non-IT content.** General-education requirements (languages, philosophy, history, physical education) and theoretical mathematics content with no direct counterpart in job market demands constitute the largest share of the surplus. Some of this content serves educational goals outside the scope of the labor market alignment metric; some may genuinely represent outdated or low-relevance course investments.

3. **Description transparency matters enormously.** Programs with full course descriptions show 5× higher alignment rates than name-only programs. This finding has methodological and policy implications: alignment cannot be accurately measured — and program quality cannot be externally assessed — without published learning outcomes.

4. **AUA shows the strongest alignment profile** among the four universities, consistent with its American-model curriculum design and the availability of rich course description data.

---

## 7.2 Contributions

This thesis makes four contributions.

**Contribution 1: First computational alignment study for Armenian IT education.** No prior study has applied automated skill extraction and taxonomy-based alignment analysis to Armenian university curricula and job market data jointly. This fills a decade-old gap in the evidence base for Armenian higher education policy, updating and extending the survey-based findings of Kupets [2] with contemporaneous, program-level data.

**Contribution 2: Multi-source Armenian IT job market dataset.** The job market dataset aggregates a 1,369-posting market snapshot from 14 sources and derives a 753-posting IT-only subset for downstream analysis. No comparable multi-source Armenian IT job dataset appears to exist in the literature. The dataset, pipeline, and documentation are archived for reproducibility and future extension.

**Contribution 3: Multilingual NLP pipeline for curriculum analysis.** The methodology handles Armenian-language input via machine translation (OpenAI gpt-4o-mini), validated at 20/20 quality against a human-rated comparator. The pipeline is documented end-to-end and can be adapted to other non-English higher education contexts where curriculum data is not in the dominant NLP language.

**Contribution 4: Evidence base for curriculum reform.** The ranked gap skills, per-program alignment scores, and description asymmetry finding provide concrete, actionable inputs for university curriculum committees and national accreditation bodies. These are not generic recommendations about "teaching more practical skills"; they are specific, ranked, data-driven findings about which competences are missing from which programs.

---

## 7.3 Recommendations

Based on the findings, four recommendations are offered.

**Recommendation 1: Update software engineering and computer science programs to include DevOps and cloud infrastructure modules.** Docker, Kubernetes, CI/CD pipelines, and cloud platform fundamentals (AWS, Azure, or GCP) appear as gap skills across multiple job sources and employer types. A single dedicated course or integration into existing systems programming or software engineering courses would address the most common gap.

**Recommendation 2: Mandate structured learning outcome publication as an accreditation requirement.** The description asymmetry finding demonstrates that programs without published course descriptions cannot be measured for alignment — which also means they cannot be held accountable for meeting any external standard. ANQA's next accreditation cycle should require machine-readable, structured learning outcome documentation for all IT programs.

**Recommendation 3: Establish a regular curriculum–labor market alignment monitoring process.** This study provides a one-time snapshot (March 2026). A sustainable alignment monitoring system — running the same pipeline annually against refreshed job posting data — would allow universities to track the gap over time and intervene before large deficits accumulate. The pipeline developed in this thesis is designed for this use: it is fully automated from the data collection stage onward.

**Recommendation 4: Distinguish general-education requirements from program-level skill content in alignment reporting.** The state-mandated general-education requirements (Armenian language, physical education, history) that appear in the curriculum surplus are not program design choices and should not be treated as program quality deficits. A more accurate alignment metric would filter these categories at the input stage and report program-level alignment separately from general-education compliance.

---

## 7.4 Future Research

Several directions emerge naturally from this work.

**NPUA inclusion.** The National Polytechnic University of Armenia was excluded due to web access restrictions. It is one of Armenia's largest technical universities. Future work should attempt to collect its curriculum data through alternative means (direct university contact, manual data entry from published program documents) and include it in the analysis.

**Longitudinal tracking.** This study is a cross-sectional snapshot. A longitudinal study collecting job posting data annually over 3–5 years would reveal whether the skill gap is growing (curricula falling further behind accelerating technology change) or shrinking (curriculum updates beginning to close the gap). It would also allow tracking of emerging skill categories like generative AI tools.

**Supervised skill extraction.** The 44% recall ceiling of TF-IDF extraction could be raised substantially by training a supervised NER model on Armenian-domain labeled data. The SkillSpan annotation framework [10] provides a replicable methodology; the main obstacle is obtaining labeled Armenian curriculum and job market sentences, which could be achieved with a crowdsourced annotation effort.

**Student-level outcomes.** This thesis measures what curricula teach and what employers demand. A natural extension is to measure what graduates actually know (via competence assessment), allowing triangulation: the gap between teaching and demand, and the additional gap between teaching and graduate competence. This would make constructive alignment failures directly observable at the individual level.

**Regional comparison.** The methodology developed here can be applied to other post-Soviet higher education systems (Georgia, Azerbaijan, Kazakhstan) with analogous structural characteristics. A comparative study would allow disentangling Armenia-specific factors from system-level post-Soviet curriculum path dependency.

---

## 7.5 Closing Remarks

The curriculum–labor market gap in Armenian IT education is real, measurable, and concentrated in specific, identifiable skill categories. It is not, however, intractable. The gap identified in this study is largely a maintenance problem — not a fundamental mismatch between what universities are capable of teaching and what employers need — but a failure to keep curriculum content synchronized with a rapidly evolving technology landscape.

The tools to close this gap exist: the technology is widely available and well-documented, the evidence of demand is visible in publicly accessible job data, and the curriculum structures needed to deliver it are already in place. What has been missing is a clear, quantitative picture of exactly where the gap is. This thesis provides that picture for the first time.

---

**Chapter references:** [2] Kupets (2016) · [10] Zhang et al. (2022)
# References

*APA 7th edition format. Numbers correspond to inline citations [n] throughout the thesis.*

---

## Citation Index

| # | Author(s) | Year | Short title |
|---|---|---|---|
| [1] | World Economic Forum | 2025 | Future of Jobs Report 2025 |
| [2] | Kupets, O. | 2016 | Skill mismatch and overeducation in transition economies |
| [3] | Aljohani et al. | 2022 | Systematic review: curriculum and labor market alignment |
| [4] | Almaleh et al. | 2019 | Align My Curriculum |
| [5] | Biggs, J. & Tang, C. | 2011 | Teaching for Quality Learning |
| [6] | Amirova, T. & Valiyev, A. | 2021 | Competence gap in Azerbaijan |
| [7] | Ahadi et al. | 2022 | Skills Taught vs Skills Sought (EDM) |
| [8] | Musazade et al. | 2026 | UniSkill dataset (LREC) |
| [9] | Grootendorst, M. | 2020 | KeyBERT |
| [10] | Zhang et al. | 2022 | SkillSpan (NAACL) |
| [11] | Reimers, N. & Gurevych, I. | 2019 | Sentence-BERT (EMNLP) |
| [12] | Wang et al. | 2020 | MiniLM (NeurIPS) |
| [13] | Autor, D.H., Levy, F. & Murnane, R.J. | 2003 | Skill content of technological change |
| [14] | European Commission | 2023 | ESCO v1.2 |
| [15] | Chiarello et al. | 2021 | Industry 4.0 skills in Wikipedia |
| [16] | SFIA Foundation | 2021 | Skills Framework for the Information Age v8 |
| [17] | Carbonell, J. & Goldstein, J. | 1998 | Maximal Marginal Relevance (SIGIR) |
| [18] | OpenAI | 2024 | GPT-4o mini |
| [19] | Pedregosa et al. | 2011 | Scikit-learn |
| [20] | Gilardi et al. | 2023 | ChatGPT outperforms crowd workers (PNAS) |
| [21] | He et al. | 2024 | Is ChatGPT a good annotator? |
| [22] | Salton, G. & Buckley, C. | 1988 | Term-weighting in automatic text retrieval (TF-IDF) |

---

## Full References

**[1]** World Economic Forum. (2025). *The future of jobs report 2025*. World Economic Forum. https://www.weforum.org/publications/the-future-of-jobs-report-2025/

**[2]** Kupets, O. (2016). *Skill mismatch and overeducation in transition economies.* IZA World of Labor, Article 224. https://wol.iza.org/articles/skill-mismatch-and-overeducation-in-transition-economies/long

**[3]** Aljohani, M., Alnafessah, A., Alhumaid, K., & Gawanmeh, A. (2022). A systematic review of research on curriculum and labor market alignment. *Journal of Innovation & Knowledge, 7*(1), 100186. https://doi.org/10.1016/j.jik.2022.100186

**[4]** Almaleh, A., Aslam, M. A., Saeedi, K., & Aljohani, N. R. (2019). Align my curriculum: A framework to bridge the gap between acquired university curriculum and required market skills. *Sustainability, 11*(9), 2607. https://doi.org/10.3390/su11092607

**[5]** Biggs, J., & Tang, C. (2011). *Teaching for quality learning at university* (4th ed.). Society for Research into Higher Education & Open University Press.

**[6]** Amirova, T., & Valiyev, A. (2021). Competence gap analysis: Employer and graduate perspectives from Azerbaijan. *Journal of Teaching and Learning for Graduate Employability, 12*(1), 117–133.

**[7]** Ahadi, A., Kitto, K., Rizoiu, M., & Musial, K. (2022). *Skills taught vs skills sought: Using skills analytics to identify the gaps between curriculum and job markets*. Poster presented at the 15th International Conference on Educational Data Mining (EDM 2022). https://doi.org/10.5281/zenodo.6853121

**[8]** Musazade, E., Mezei, J., & Zhang, H. (2026). UniSkill: A dataset for linking university courses to ESCO skills. *Proceedings of the 2026 Language Resources and Evaluation Conference (LREC)*. arXiv:2603.03134

**[9]** Grootendorst, M. (2020). *KeyBERT: Minimal keyword extraction with BERT* [Software]. Zenodo. https://doi.org/10.5281/zenodo.4461265

**[10]** Zhang, M., Jensen, K., Sonnenschein, H., Brekke, A. S., & Plank, B. (2022). SkillSpan: Hard and soft skill extraction from English job postings. In *Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL 2022)* (pp. 4962–4984). https://doi.org/10.18653/v1/2022.naacl-main.366

**[11]** Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (pp. 3982–3992). https://doi.org/10.18653/v1/D19-1410

**[12]** Wang, W., Wei, F., Dong, L., Bao, H., Yang, N., & Zhou, M. (2020). MiniLM: Deep self-attention distillation for task-agnostic compression of pre-trained transformers. In *Proceedings of the 34th Conference on Neural Information Processing Systems (NeurIPS 2020)*. arXiv:2002.10957

**[13]** Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. *The Quarterly Journal of Economics, 118*(4), 1279–1333. https://doi.org/10.1162/003355303322552801

**[14]** European Commission. (2023). *ESCO: European skills, competences, qualifications and occupations* (v1.2). Publications Office of the European Union. https://esco.ec.europa.eu/

**[15]** Chiarello, F., Trivelli, L., Bonaccorsi, A., & Fantoni, G. (2021). Towards ESCO 4.0 — Is the European classification of skills in line with Industry 4.0? *Technological Forecasting and Social Change, 173*, 121177. https://doi.org/10.1016/j.techfore.2021.121177

**[16]** SFIA Foundation. (2021). *Skills framework for the information age* (v8). https://sfia-online.org/

**[17]** Carbonell, J., & Goldstein, J. (1998). The use of MMR, diversity-based reranking for reordering documents and producing summaries. In *Proceedings of the 21st Annual International ACM SIGIR Conference* (pp. 335–336). https://doi.org/10.1145/290941.291025

**[18]** OpenAI. (2024). *GPT-4o mini* [Language model]. https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/

**[19]** Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., … Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.

**[22]** Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management, 24*(5), 513–523. https://doi.org/10.1016/0306-4573(88)90021-0

**[20]** Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences, 120*(30), e2305016120. https://doi.org/10.1073/pnas.2305016120

**[21]** He, X., Lin, Z., Gong, Y., Jin, H., Han, T., Mou, X., … Dolan, B. (2024). AnnoLLM: Making large language models to be better crowdsourced annotators. *Proceedings of NAACL 2024 (Industry Track)*. arXiv:2303.16854

---

## Data Sources and Tools

- Apify, Inc. (2026). *Apify web scraping platform* [Software]. https://apify.com/
- Python Software Foundation. (2023). *Python* (version 3.11) [Software]. https://www.python.org/
- LinkedIn Corporation. (2026). *LinkedIn job postings, Armenia* [Dataset, accessed March 2026]. https://linkedin.com/
- Staff.am. (2026). *Staff.am job listings* [Dataset, accessed March 2026]. https://staff.am/
- job.am. (2026). *job.am listings* [Dataset, accessed March 2026]. https://job.am/

---

*Total: 21 academic references + data/tool citations.*
