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
