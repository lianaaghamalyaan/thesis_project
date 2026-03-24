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

The knowledge/competence split in the ESCO overlap reinforces this interpretation. Of the 133 overlapping ESCO concepts (TF-IDF), 70% are classified as *knowledge* and 30% as *skill/competence*. The gap is approximately balanced (48% knowledge, 51% applied competence). Armenian curricula are stronger on the knowledge transmission side of the task spectrum and weaker on applied competence — precisely where the task-based framework predicts the largest market premium.

### 6.2.3 ESCO Lens: Structural Coverage and Emerging Skills

The ESCO-normalized results reveal two analytically distinct layers of the alignment picture.

The first layer is **structural coverage within the ESCO vocabulary**. Armenian IT curricula cover 329 unique ESCO concepts (TF-IDF) against a job market demand of 527 — a 25.2% overlap. This means that roughly three in four employer-demanded ESCO concepts have no representation in any Armenian IT curriculum. The gap is not concentrated in exotic or niche areas: it includes Java (demanded in 1.9% of all postings), TypeScript (1.8%), PHP (1.6%), and CSS (0.8%) — mainstream technologies taught in the majority of Western software engineering programs.

The second layer is **emerging skills beyond ESCO**. The supplementary tech lexicon analysis identified 24 specific modern tools absent from both ESCO v1.2 and from curricula. Azure (25 postings), React (25), AWS (15), Kubernetes (7), Docker (4), and Terraform (6) all have zero curriculum presence. LLM/GenAI tools (19 postings) and Node.js (17) are the only emerging categories with any curriculum representation (4 and 3 courses respectively), suggesting limited early adoption. The absence of cloud platforms, containerization, and infrastructure-as-code from curricula while these tools appear in double-digit percentages of job postings represents the most concrete and time-sensitive curriculum reform target.

### 6.2.4 Synthesis: A Coherent Picture Across Three Lenses

All three frameworks converge on the same diagnosis. Constructive alignment identifies the absence of ILO review against labor market standards. The task-based framework identifies a systematic underinvestment in non-routine applied competences. ESCO normalization quantifies the gap as concentrated in applied tool-level skills that have been in stable market demand for over a decade.

The structural pattern that emerges is: Armenian IT curricula are well-aligned with the *knowledge* layer of the job market (shared subject domains — algorithms, data structures, programming foundations, databases) but systematically lag in the *applied competence* layer (specific tools, workflows, and deployment practices). This gap is not random or idiosyncratic — it follows the boundary between formal academic content and professional practice. It is a gap that structured industry engagement, capstone projects, and curriculum co-design with employers could plausibly close.

---

## 6.3 Addressing the Research Questions

### RQ1: Most frequently demanded skills in the Armenian IT job market

The most frequently demanded skills in the Armenian IT job market, as identified by TF-IDF extraction from 1,068 job postings, cluster into four categories:

1. **Programming languages and platforms:** Python, JavaScript, Java, SQL, .NET, TypeScript
2. **Modern software delivery tools:** Docker, Kubernetes, CI/CD, Git, Terraform, Ansible
3. **Cloud and infrastructure:** AWS, Azure, Google Cloud, cloud architecture, microservices, REST APIs
4. **Core competences:** algorithms, data structures, testing, software design, Agile, DevOps

The source composition of the dataset shapes this demand signal. LinkedIn (734 postings, 68.7%) skews toward senior and mid-level roles in international company Armenia offices. SoftConstruct (141 postings, 13.2%) introduces domain-specific gaming and betting industry demand — notably, ESCO concepts such as *betting*, *gambling games*, and *manage casino* appear in the top gap list precisely because SoftConstruct is the largest single non-aggregator employer source. These domain-specific demands are reported in full but should be understood as employer-specific rather than sector-wide IT requirements. Filtering them out does not materially change the top 10 IT-specific gap skills (Java, TypeScript, PHP, DevOps, CI/CD, REST APIs, Docker, Kubernetes, CSS, Android).

### RQ2: Most prevalent competences in Armenian IT curricula

The most prevalent skills in Armenian IT curricula reflect the composition of the university sample. YSU, contributing 59.5% of courses, dominates the curriculum vocabulary. Frequent curriculum concepts include: algorithms, computer science foundations, data structures, programming (Python, C++, Java), databases, mathematical analysis, networks, and software engineering fundamentals.

AUA shows the highest density of applied technical content per course, consistent with its American-model pedagogy and fully available course descriptions. YSU has broader theoretical coverage but lower applied technology density per course. The overlap in extracted ESCO concepts between AUA and YSU reflects genuine pedagogical similarity in foundational content, despite their different institutional models.

NUACA and RAU, with name-only course records, yield the most conservative skill profiles. The finding that 48% of NUACA courses and 56% of RAU courses produce zero ESCO concept assignments — compared to 12% for AUA — is primarily a measurement limitation (description asymmetry) rather than a finding about curricular content. However, it is also consistent with programs that are less documentation-transparent and may have less structured learning outcome specification.

### RQ3: Overall alignment magnitude

The pre-ESCO baseline alignment rate is 6.4% (TF-IDF string match) and 0.26% (KeyBERT). These figures substantially underestimate true conceptual alignment due to synonymous phrasing — a phrase pair like "object oriented programming" and "OOP principles" counts as non-overlapping at the string level.

After ESCO normalization, the alignment rises to **25.2%** (TF-IDF), **20.3%** (KeyBERT), and **25.7%** (union of both methods). All three estimates are robust across the 0.70–0.80 threshold range: lowering the threshold adds matched phrases but not new ESCO concepts, confirming the bottleneck is ESCO vocabulary coverage rather than calibration sensitivity.

The 25.2% figure means that approximately one in four skills expressible in ESCO v1.2 that employers demand is covered somewhere across Armenian IT curricula. This figure is best interpreted as a lower bound, for two reasons: (1) ESCO v1.2 does not contain many modern tools that are both demanded and potentially taught (Docker, React, Azure), and (2) NUACA and RAU scores are structurally suppressed by name-only description coverage. Adjusting for these factors, the true alignment is likely meaningfully higher — but the present methodology cannot produce a precise adjusted estimate.

### RQ4: Programs with strongest and weakest alignment

The per-program ESCO-normalized results confirm the structural hypotheses:

- **AUA programs lead** (5.77% average coverage). AUA Computer and Information Science (Master) achieves 9.1%, AUA Computer Science (Bachelor) 7.2%. AUA's advantage reflects fuller course descriptions and an applied-technology-oriented curriculum.
- **YSU programs cluster in the middle** (4.46% average). Data Science in Business (5.7%), Information Systems Development (5.5%), and Applied Statistics programs (5.3–5.5%) lead the YSU group. The theoretically oriented programs — Discrete Mathematics and Theoretical Informatics (2.85%), Numerical Analysis and Mathematical Modelling (2.85%), Blockchain and Digital Currencies (1.71%) — rank lower.
- **NUACA programs occupy the lower range** (1.60% average, 0.57%–2.47%). This reflects both name-only data and a curriculum oriented toward architecture, construction, and geographic information systems rather than software industry practice.
- **RAU's single program** aligns at 2.28%, above NUACA but below most YSU programs, consistent with its strong theoretical mathematics orientation.

The 15-fold spread between best (9.1%) and worst (0.57%) program confirms that alignment varies more within institutions than between them. Degree level (Bachelor vs. Master) is not a significant predictor (4.36% vs. 3.88%), indicating that graduate programs are not systematically better aligned with market demand than undergraduate ones. This is notable: it suggests that the curriculum gap is not primarily a matter of educational level but of curriculum design priorities.

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

**ESCO vocabulary lag.** ESCO v1.2 does not contain Docker, Kubernetes, React, Azure, and other tools in active professional use. The 12.6% phrase match rate (only 2,523 of 19,998 unique phrases match ESCO) reflects this structural vocabulary gap. The 25.2% coverage figure understates true alignment for the most modern technology layers of both curricula and job postings.

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
