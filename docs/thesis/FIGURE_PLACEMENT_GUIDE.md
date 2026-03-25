# Figure Placement Guide

This file lists all recommended figures for the thesis, with exact placement locations and descriptions.
Figures marked ✓ already exist as notebook outputs in `data/processed/`. Figures marked ★ need to be created or exported.

---

## Chapter 1: Introduction

**Figure 1.1 — Armenian IT sector growth (suggested)**
- Location: After the first paragraph of Section 1.1 (after "further progress [1].")
- Content: Bar chart showing growth of Armenian IT exports 2015–2025 (use World Bank / ITEK data)
- Status: ★ Create from public data if available

---

## Chapter 3: Theoretical Framework

**Figure 3.1 — Integrated Framework Diagram**
- Location: Section 3.5, replace the ASCII diagram with a proper figure
- Content: Clean flowchart showing the three-framework integration (Biggs & Tang → Curriculum ILOs ↔ Labor market tasks → ESCO normalization → Gap analysis)
- Status: ★ Create in draw.io / Lucidchart / PowerPoint and export as PNG
- Caption: *Figure 3.1. Integrated theoretical framework: constructive alignment, task-based skill demand, and ESCO normalization.*

---

## Chapter 4: Methodology

**Figure 4.1 — NLP Pipeline Overview**
- Location: Section 4.1, after the pipeline code block (after "end-to-end reproducibility.")
- Content: Clean horizontal pipeline flowchart with 6 stages (Data Collection → Processing → Translation → Skill Extraction → ESCO Normalization → Alignment Analysis), each with key methods labeled
- Status: ★ Create as a diagram
- Caption: *Figure 4.1. End-to-end NLP pipeline for curriculum–labor market alignment analysis.*

**Figure 4.2 — University Description Coverage**
- Location: Section 4.5.7.1, after Table 4.7
- Content: Stacked bar chart showing % of courses with descriptions by university (AUA 97%, YSU 100%, NUACA 0%, RAU 0%)
- Status: ★ Simple chart, easy to create
- Caption: *Figure 4.2. Course description availability by university. AUA and YSU have rich descriptions; NUACA and RAU have none.*

**Figure 4.3 — ESCO Threshold Calibration Curve**
- Location: Section 4.5.6, after the F1/threshold description
- Content: Line chart of Precision, Recall, and F1 at thresholds 0.60, 0.65, 0.70, 0.75, 0.80, 0.85. Peak F1 at 0.75 should be visually clear.
- Source: `notebooks/3_analysis/04_esco_calibration.ipynb` outputs
- Status: ✓ Data exists — export from notebook as PNG
- Caption: *Figure 4.3. Precision, recall, and F1 across cosine similarity thresholds for ESCO matching. Threshold 0.75 yields maximum F1 = 0.711.*

---

## Chapter 5: Results

**Figure 5.1 — Pre-ESCO vs Post-ESCO Coverage (method comparison)**
- Location: Start of Section 5.2 (ESCO normalization results), before Table 5.x
- Content: Grouped bar chart: TF-IDF and KeyBERT side by side, showing pre-ESCO (8.85%, 0.33%) vs post-ESCO (32.82%, 28.5%) coverage rates
- Source: Computed results
- Status: ★ Create simple bar chart
- Caption: *Figure 5.1. Coverage rate before and after ESCO normalization. ESCO normalization raises TF-IDF coverage from 8.85% to 32.82% by resolving surface-form variation.*

**Figure 5.2 — Per-Program Alignment Heatmap**
- Location: Section 5.3 (per-program results), after the program-level table
- Content: Heatmap with programs on y-axis, metric (coverage rate) as color, grouped by university. Existing notebook output.
- Source: `notebooks/3_analysis/06_alignment_analysis.ipynb` — the per-program coverage visualization
- Status: ✓ Exists in notebook — export as PNG
- Caption: *Figure 5.2. ESCO-normalized coverage rates by program and university (TF-IDF method). Color intensity reflects alignment strength.*

**Figure 5.3 — Top Gap Skills (Bar Chart)**
- Location: Section 5.4 (gap analysis), alongside or after the gap skills table
- Content: Horizontal bar chart of top 20 gap skills ranked by job posting frequency
- Source: `data/processed/esco/skill_frequency_overall.csv`
- Status: ✓ Exists in notebook — export as PNG
- Caption: *Figure 5.3. Top 20 employer-demanded skills absent from Armenian IT curricula, ranked by frequency across the IT-only job-market subset.*

**Figure 5.4 — Skill Overlap Venn Diagram**
- Location: Section 5.2 overview, before the gap/surplus breakdown
- Content: Two-circle Venn diagram: Curriculum skills (C), Job market skills (J), overlap, gap, and surplus regions labeled with counts
- Status: ★ Simple to create with matplotlib or draw.io
- Caption: *Figure 5.4. ESCO concept set relationships: curriculum (C = 332), job market (J = 326), overlap (107), gap (219), surplus (225).*

**Figure 5.5 — Top Skills by IT Role (heatmap)**
- Location: Section 5.5 (role-level analysis)
- Content: Heatmap of top 15 skills × 9 IT roles
- Source: `data/processed/esco/skills_by_role.csv` — existing notebook output
- Status: ✓ Exists in notebook — export as PNG
- Caption: *Figure 5.5. Top demanded skills across nine IT role categories in the Armenian job market.*

---

## Chapter 6: Discussion

**Figure 6.1 — Knowledge vs. Competence Split**
- Location: Section 6.2.3, after the knowledge-versus-competence finding
- Content: Stacked bar chart showing ESCO concept type breakdown (knowledge vs. skill/competence) for: Overlap set, Gap set, Surplus set
- Status: ★ Data in notebook outputs, create visualization
- Caption: *Figure 6.1. ESCO concept type composition of the overlap, gap, and surplus sets. The overlap is knowledge-dominant (77.6%); the gap is slightly competence-dominant (51.1%).*

---

## Quick Export Instructions

For figures already in notebooks (✓ status):
1. Open the relevant notebook in Jupyter
2. Find the cell that produces the visualization
3. Right-click the output → "Save Image As" (or add `plt.savefig('figure_X.png', dpi=150, bbox_inches='tight')` before `plt.show()`)
4. Save to `docs/thesis/figures/`

For figures needing creation (★ status):
- Figures 3.1 and 4.1: Use draw.io (free at draw.io), export as PNG
- All bar charts: Use the existing notebooks or create a new `07_figures.ipynb`
- Figure 5.4 (Venn): Use `matplotlib_venn` library (`pip install matplotlib-venn`)
