# Chapter 1: Introduction

## 1.1 Background and Motivation

The Information Technology (IT) sector in Armenia has expanded rapidly over the past decade, becoming a cornerstone of the national economy. This growth—fueled by rising international investment and the emergence of vibrant local tech clusters—has created a constant demand for highly skilled professionals. However, as the industry moves toward complex fields like Data Engineering, Machine Learning, and Cloud Computing, the availability of industry-ready graduates has become a critical bottleneck for further progress (World Economic Forum, 2025).

While Armenian universities offer structured academic programs grounded in computer science and applied mathematics, there is a persistent disconnect between formal instruction and the technical competencies employers require. Research by Kupets (2016) shows that approximately 30% of urban workers in Armenia are overeducated for their current roles, yet 69.9% of these workers feel their formal education has limited practical use. This structural pattern, rooted in post-Soviet educational path dependency, results in a costly paradox: a skill gap that delays graduate entry into the workforce and stifles growth in a sector that reports thousands of unfilled vacancies despite high graduate numbers (Kupets, 2016). Understanding this gap through quantitative, reproducible evidence is the first step toward improving educational outcomes and ensuring graduates are truly equipped for a rapidly evolving labor market.

## 1.2 Problem Statement

At the heart of this research is the lack of structured, data-driven analysis regarding the alignment between IT higher education and the labor market in Armenia. Currently, most discussions of the "skill gap" rely on qualitative surveys or anecdotal employer feedback rather than systematic, objective measurement (Aljohani et al., 2022). Without a detailed comparison of actual course content against real-world job specifications, it is nearly impossible to identify exactly which competencies are missing from curricula or which courses have lost their market relevance. This study addresses this information deficit by performing a large-scale, automated analysis of university curriculum data and job market postings to identify areas of divergence and alignment with empirical precision.

## 1.3 Research Objectives

The primary goal of this thesis is to provide a quantitative assessment of how well Armenian university IT curricula match the current demands of the domestic job market. To achieve this, the following objectives have been established:

1. To build a structured curriculum dataset by collecting and processing data from 25 programs across four major Armenian universities: Yerevan State University (YSU), the American University of Armenia (AUA), the National University of Architecture and Construction of Armenia (NUACA), and the Russian-Armenian University (RAU).
2. To aggregate a comprehensive job market dataset from 11 diverse sources, including job aggregators (LinkedIn, Staff.am, job.am) and direct company career portals (EPAM, SoftConstruct, Picsart, Krisp, and others), covering 1,068 postings active in Armenia as of March 2026 after deduplication.
3. To implement a Natural Language Processing (NLP) pipeline for automated skill extraction from 1,161 curriculum records and 1,068 job postings, handling multilingual content (Armenian, English, and Russian).
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

2. **Multi-source job dataset.** By aggregating 1,068 deduplicated postings from 11 distinct sources—combining broad aggregators with direct employer portals—this research provides a more representative picture of the Armenian IT labor market than any single-source approach.

3. **Multilingual NLP pipeline.** The methodology is designed to address the challenge of Armenian-language curriculum data (691 of 1,161 course records) alongside English and Russian sources, providing a replicable model for curriculum alignment research in other non-English educational contexts.

4. **Evidence base for curriculum reform.** The study delivers program-level alignment scores and a ranked list of in-demand skills currently absent from curricula. These results provide concrete, actionable inputs for university committees and national accreditation bodies like ANQA.

This work builds on the methodological precedent of Almaleh et al. (2019), who applied a similar computational framework in the Saudi Arabian context, and extends it to a unique geographic and linguistic setting.

## 1.6 Scope and Limitations

The analysis covers four Armenian universities for which structured, publicly accessible curriculum data was available at the time of collection (March 2026): YSU, AUA, NUACA, and RAU. The National Polytechnic University of Armenia (NPUA)—one of the country’s largest technical universities with approximately ten IT-related programs—could not be included because its official website blocks automated data access through Cloudflare protections. The Université Française en Arménie (UFAR) was identified but not assessed within the scope of this project. At RAU, data collection was limited to one bachelor-level program. While these exclusions affect the overall representativeness of the curriculum side of the analysis, they are acknowledged as limitations and discussed in detail in Chapter 4.

The job market dataset represents a cross-sectional snapshot of postings active in Armenia in March 2026 and thus does not capture long-term trends in skill demand.

## 1.7 Structure of the Thesis

The remainder of this thesis is organized as follows. Chapter 2 reviews current literature on curriculum–labor market alignment, NLP-based skill extraction, and the specific Armenian educational context. Chapter 3 outlines the theoretical framework, grounding the analysis in constructive alignment theory (Biggs & Tang, 2011) and using ESCO as the operational layer for skill measurement. Chapter 4 provides a detailed description of the data collection methodology, dataset characteristics, and the NLP analysis pipeline. Chapter 5 presents the empirical findings, including alignment metrics, per-university results, and the identified skill gap. Chapter 6 discusses these findings in relation to the initial research questions and existing literature. Finally, Chapter 7 concludes with a summary of contributions, practical recommendations, and directions for future research.

---

*[DRAFT STATUS: citations are indicated by author/year — full references to be formatted in final bibliography. ⚠️ = verify before submission.]*

*Citation checklist for this chapter:*
- *Kupets (2016) — IZA World of Labor, verified ✓*
- *World Economic Forum (2025) — Future of Jobs Report, verified ✓*
- *Aljohani et al. (2022) — Journal of Innovation & Knowledge, verified ✓*
- *Almaleh et al. (2019) — Sustainability, verified ✓*
- *Biggs & Tang (2011) — Teaching for Quality Learning, verified ✓*
- *ANQA — Armenian National Quality Assurance body, add URL in references*
