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
