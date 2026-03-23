# Chapter 7: Conclusion

*[DRAFT STATUS — structure complete. Finalize after ESCO normalization and per-program results are available.]*

---

## 7.1 Summary of the Study

This thesis set out to answer one question: how well do Armenian IT university curricula align with the skill demands of the Armenian IT labor market? To answer it, a five-stage NLP pipeline was constructed, applied to a purpose-built dataset of 1,161 curriculum courses from 25 programs across four universities and 1,068 unique job postings from 11 sources — the first dataset of its kind for the Armenian context.

The pipeline produced two types of results. The first is a pre-ESCO baseline: a raw string-level overlap of 6.4% (TF-IDF) between the curriculum and job market skill vocabularies. This figure is a lower bound, suppressed by the synonymous phrasing problem that ESCO normalization is designed to resolve. The second type — ESCO-normalized per-program alignment scores — is the primary output of the study and will be finalized after the manual calibration step is complete.

Regardless of the exact ESCO-normalized figure, the structural findings are clear:

1. **The skill gap is real and concentrated.** Employer-demanded DevOps and cloud infrastructure skills — Docker, Kubernetes, CI/CD, Terraform, cloud platforms — are consistently absent from curriculum text. These are not emerging technologies; they have been in professional use for over a decade. Their absence reflects a structural lag in curriculum update cycles.

2. **The curriculum carries significant non-IT content.** General-education requirements (languages, philosophy, history, physical education) and theoretical mathematics content with no direct counterpart in job market demands constitute the largest share of the surplus. Some of this content serves educational goals outside the scope of the labor market alignment metric; some may genuinely represent outdated or low-relevance course investments.

3. **Description transparency matters enormously.** Programs with full course descriptions show 5× higher alignment rates than name-only programs. This finding has methodological and policy implications: alignment cannot be accurately measured — and program quality cannot be externally assessed — without published learning outcomes.

4. **AUA shows the strongest alignment profile** among the four universities, consistent with its American-model curriculum design and the availability of rich course description data.

---

## 7.2 Contributions

This thesis makes four contributions.

**Contribution 1: First computational alignment study for Armenian IT education.** No prior study has applied automated skill extraction and taxonomy-based alignment analysis to Armenian university curricula and job market data jointly. This fills a decade-old gap in the evidence base for Armenian higher education policy, updating and extending the survey-based findings of Kupets (2016) with contemporaneous, program-level data.

**Contribution 2: Multi-source Armenian IT job market dataset.** The job market dataset aggregates 1,068 unique postings from 11 sources — three aggregators and eight company portals — collected and deduplicated in March 2026. No comparable multi-source Armenian IT job dataset appears to exist in the literature. The dataset, pipeline, and documentation are archived for reproducibility and future extension.

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

**Supervised skill extraction.** The 44% recall ceiling of TF-IDF extraction could be raised substantially by training a supervised NER model on Armenian-domain labeled data. The SkillSpan annotation framework (Zhang et al., 2022) provides a replicable methodology; the main obstacle is obtaining labeled Armenian curriculum and job market sentences, which could be achieved with a crowdsourced annotation effort.

**Student-level outcomes.** This thesis measures what curricula teach and what employers demand. A natural extension is to measure what graduates actually know (via competence assessment), allowing triangulation: the gap between teaching and demand, and the additional gap between teaching and graduate competence. This would make constructive alignment failures directly observable at the individual level.

**Regional comparison.** The methodology developed here can be applied to other post-Soviet higher education systems (Georgia, Azerbaijan, Kazakhstan) with analogous structural characteristics. A comparative study would allow disentangling Armenia-specific factors from system-level post-Soviet curriculum path dependency.

---

## 7.5 Closing Remarks

The curriculum–labor market gap in Armenian IT education is real, measurable, and concentrated in specific, identifiable skill categories. It is not, however, intractable. The gap identified in this study is largely a maintenance problem — not a fundamental mismatch between what universities are capable of teaching and what employers need — but a failure to keep curriculum content synchronized with a rapidly evolving technology landscape.

The tools to close this gap exist: the technology is widely available and well-documented, the evidence of demand is visible in publicly accessible job data, and the curriculum structures needed to deliver it are already in place. What has been missing is a clear, quantitative picture of exactly where the gap is. This thesis provides that picture for the first time.

---

*Citation checklist for this chapter:*
- *Kupets (2016) — IZA World of Labor, verified ✓*
- *Zhang et al. (2022) — SkillSpan, NAACL, verified ✓*
- *ANQA — Armenian National Quality Assurance body — add URL in references*
