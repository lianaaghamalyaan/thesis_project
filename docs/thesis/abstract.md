# Abstract

This thesis presents the first large-scale, computational analysis of the alignment between IT university curricula and labor market skill demands in Armenia. Four Armenian universities — Yerevan State University (YSU), the American University of Armenia (AUA), the National University of Architecture and Construction of Armenia (NUACA), and the Russian-Armenian University (RAU) — are examined alongside 1,068 job postings collected from 11 sources active in Armenia in March 2026.

A five-stage NLP pipeline is constructed: (1) data collection and structuring; (2) multilingual preprocessing including Armenian-to-English translation of 691 YSU course records; (3) automated skill extraction using TF-IDF and KeyBERT (all-MiniLM-L6-v2); (4) normalization of extracted skill phrases against the ESCO v1.2 taxonomy via cosine similarity; and (5) alignment analysis producing per-program coverage rates, gap sets, and surplus sets.

Pre-ESCO baseline results indicate a raw string overlap of 6.4% (TF-IDF) and 0.26% (KeyBERT) between curriculum and job market skill vocabularies — figures that substantially underestimate true alignment due to synonymous phrasing. After ESCO normalization, coverage rises to 25.2% (TF-IDF) and 20.3% (KeyBERT), with a union estimate of 25.7%. The overlap is dominated by knowledge concepts (70%) over applied competences (30%), while the gap is predominantly applied (51%), indicating that curricula cover relevant subject domains but fall short on practice-oriented content. Sensitivity analyses confirm a 5× coverage advantage for programs with full course descriptions (AUA) over name-only programs (YSU), and a 44% soft recall against human-curated skill tags from 151 job postings. Key skill gaps include DevOps tooling (Docker, Kubernetes, CI/CD), cloud infrastructure (AWS, Azure), and modern web frameworks (React, TypeScript); key curriculum-only content includes general-education subjects (philosophy, history, foreign languages) and theoretical mathematics with limited direct market relevance.

The thesis contributes: a reusable methodology for curriculum–labor market alignment analysis in multilingual, data-scarce contexts; the first structured IT curriculum dataset for Armenian higher education; and an evidence base for targeted curriculum reform in a rapidly growing IT sector that has not previously been studied at this scale or precision.

---

**Keywords:** curriculum alignment, skill gap analysis, NLP, TF-IDF, KeyBERT, ESCO, Armenian IT education, labor market, skill extraction

---

*Supervisor: [supervisor name]*
*Program: [program name]*
*Institution: [institution]*
*Year: 2026*
