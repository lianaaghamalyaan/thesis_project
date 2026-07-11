# Information Architecture — CurriculumLens

## Navigation model

The product is program-first. Every entry point starts with selecting a university context, then a program. University context is set at login (Phase 2) or at the app level for Phase 1 MVP (defaulting to YSU).

### Top-level navigation

```
Overview
Programs
  └─ [Program Detail]
       └─ [Job Fit Comparison]
Recommendations
Evidence
Admin
```

The sidebar should show the university name and logo as context. The active program, if one is selected, persists in a breadcrumb or secondary nav.

---

## Page 1 — Overview

**Purpose:** Show the portfolio health of all programs for the selected university at a glance. Give academic leadership a one-screen status summary.

**Who uses it:** Vice-rector, QA staff, curriculum committee chairs

**What it shows:**
- University name and context header
- Total programs, mean alignment score across programs, data snapshot date
- A ranked bar chart of all programs by core alignment score (strongest to weakest)
- Color coding: green (strong, >50%), amber (moderate, 25-50%), red (low, <25%) — with explanation that scores reflect market coverage, not program quality in absolute terms
- A "spotlight" panel: top 3 programs by score, top 3 programs with the biggest documented gaps
- Quick link to Recommendations page
- Data freshness notice: "Based on [N] IT job postings collected in [month year]"

**What it does not show:**
- Experiment comparison
- Method comparison
- Raw data tables
- Individual course lists

---

## Page 2 — Programs

**Purpose:** Browse and filter all programs for the selected university. Entry point for drilling into a specific program.

**Who uses it:** Program directors looking for their program; QA staff comparing programs

**What it shows:**
- Filterable, sortable table of programs with columns:
  - Program name
  - Degree level (Bachelor / Master)
  - Alignment score (core role-aware coverage %)
  - Relevant roles (role groups this program is compared against)
  - Gap count (number of high-frequency skills not covered)
  - Gap type signal (documentation risk: high / medium / low)
- Clicking a program opens the Program Detail page
- Filter by degree level, role group, score range

**What it does not show:**
- Raw skill lists
- Course lists
- Experiment names

---

## Page 3 — Program Detail

**Purpose:** The core product page. Explain a single program's alignment in depth — what is strong, what is missing, why the score is what it is, and what to do.

**Who uses it:** Program directors, curriculum committees, QA staff

### 3.1 Header

- Program name, degree level, university
- Breadcrumb: Overview > Programs > [Program Name]
- Last updated: data snapshot date

### 3.2 Score panel

- Primary metric: **Core role-aware coverage** displayed prominently (e.g., "47%")
- Supporting context: "This program covers approximately [N] of the [M] skills commonly required in [role group] roles in the Armenian IT market."
- Brief interpretation:
  - "This score reflects how thoroughly course descriptions document skills that appear in job postings."
  - "A higher score means more alignment; a lower score may reflect curriculum gaps, documentation gaps, or both."
- Relevant roles: list of role groups this program is compared against

### 3.3 Strengths panel

- Heading: "What this program covers well"
- Top 10-15 skills where the program has clear, high-confidence alignment
- Organized by category (e.g., Programming Fundamentals, Data Analysis, etc.) if possible
- Framing: "These foundations are well-represented in course descriptions and are in market demand."

### 3.4 Gaps panel

- Heading: "Skills missing from this program"
- Top 15-25 gap skills, ranked by job market frequency (how often they appear in job postings)
- For each gap skill, show:
  - Skill name
  - Job frequency (how many postings require it)
  - Gap type indicator (see below)

#### Gap type indicator

Each gap skill gets one of three labels:

| Label | Meaning | Visual |
|---|---|---|
| **Likely curriculum gap** | Skill is absent and course descriptions provide no evidence of related content | Red dot |
| **Possible documentation gap** | Skill may be covered but course descriptions are vague or incomplete | Amber dot |
| **Uncertain** | Low confidence in either direction | Grey dot |

This is derived from `course_confidence_tiers.json`. The logic:
- If the program has courses with high-confidence skill mappings in adjacent areas but the specific skill is absent → likely curriculum gap
- If the program has courses with low-confidence or generic descriptions in the relevant area → possible documentation gap
- If a course description is absent or very short → documentation gap flag

**Copy for UI:** "Skills marked 'possible documentation gap' may already be taught but are not clearly described in course syllabi. Updating course descriptions may improve this program's measured alignment without changing the curriculum."

### 3.5 Recommendations panel

- Heading: "Suggested next steps"
- 3-5 concrete, framed recommendations, e.g.:
  - "Consider adding or strengthening coverage of [Skill X] — it appears in [N] job postings for [role group] roles."
  - "Review course descriptions for [Course Y] and [Course Z] — these may already cover [Skill A] but it is not documented."
  - "The program's [theoretical foundations] are strong. The main gap is in applied tooling — consider adding practical labs or electives."
- Clear caveat: "These suggestions are based on automated analysis of job postings and course descriptions. They are decision-support, not prescriptions."

### 3.6 Coverage breakdown (secondary)

- Four metrics shown together with brief labels:
  - Full market coverage (vs. all IT jobs)
  - Role-aware coverage (vs. relevant role jobs)
  - Core role-aware coverage (primary, vs. core roles)
  - Weighted core coverage (frequency-weighted)
- A brief tooltip or explainer for each metric

### 3.7 Quick access to Job Fit

- "Compare this program against a specific job role →" link to the Job Fit page with this program pre-selected

---

## Page 4 — Job Fit Comparison

**Purpose:** Compare a program against a specific job role or role group. This is the highest-priority stakeholder-requested feature.

**Who uses it:** Program directors trying to understand how graduates would perform in specific roles; curriculum committees considering specializations

### 4.1 Selection panel

- Program selector (defaults to the program from Program Detail if coming from there)
- Target selector:
  - **Option A:** Select a role group (e.g., "Data / ML / AI", "Software Engineering")
  - **Option B (later):** Paste a job description (Phase 2+ — requires LLM at query time)
- The comparison runs against all IT job postings in the selected role group

### 4.2 Match overview

- "Match score" — what percentage of skills demanded by this role group are covered by the program
- Framing: "This program covers [N] of [M] skills commonly required in [role group] job postings."
- Visual: simple gauge or bar showing match %

### 4.3 Matched skills

- Heading: "What this program already covers for this role"
- List of skills present in both the program and the role's job postings
- Organized by frequency (most-demanded first)

### 4.4 Missing skills

- Heading: "Skills this role commonly requires that are not in this program"
- Ranked by job frequency
- Gap type indicator (same as Program Detail page)
- Top 15-20 skills shown by default, expandable

### 4.5 Role context

- Brief market context for the selected role:
  - Number of job postings in that role group in the dataset
  - Top 3 companies hiring for this role
  - Common seniority levels

### 4.6 Action framing

- "What this means": paragraph framing what the gap means practically
- "Suggested actions": 2-3 targeted recommendations for this specific role fit
- Link back to Program Detail

---

## Page 5 — Recommendations

**Purpose:** A cross-program priority view of the most actionable improvement opportunities for the university.

**Who uses it:** Vice-rector, curriculum committee chairs deciding where to focus effort

**What it shows:**
- Top curriculum gaps shared across multiple programs (high-frequency skills missing broadly)
- Top documentation gap opportunities (programs where description improvement alone could raise scores)
- Priority matrix: effort vs. impact framing (documentation gaps = lower effort; curriculum changes = higher effort)
- Filter by program, degree level, role group

**What it does not show:**
- Individual course breakdowns
- Methodology
- Per-job data

---

## Page 6 — Evidence

**Purpose:** Explain how results were computed. Build institutional trust. Allow traceability.

**Who uses it:** QA staff, any user who wants to understand "why this score"

**What it shows:**
- Data snapshot description:
  - Job data: [N] IT job postings, collected [date range], from [sources list]
  - Curriculum data: [N] courses, [N] programs, collected [date]
- Method summary (plain language, not academic):
  - "Skills were extracted from course descriptions using an AI language model."
  - "Skills were matched against a standardized taxonomy (ESCO v1.2)."
  - "Alignment is measured as the percentage of job-required skills that appear in the program's courses."
- Confidence note:
  - "Courses with detailed, specific descriptions are analyzed more reliably. Programs with short or vague descriptions may show lower scores than their actual curriculum quality."
- Limitations:
  - "This system measures what is documented, not everything that is taught."
  - "Results reflect a snapshot of the Armenian IT job market. They should be interpreted in that context."
- Technical evidence (expandable/collapsible):
  - Experiment name: `LLM_desc_semantic`
  - ESCO version: v1.2
  - Run date: [date]
  - Calibration summary: 293 pairs, 94.3% human agreement
- Download: ability to export the evidence summary as PDF for committee documentation

---

## Page 7 — Admin / Data Freshness

**Purpose:** Show the data state and pipeline health. Allow authorized users to see when data was last collected and when the next refresh is due.

**Who uses it:** System administrator, QA staff, technical contacts

**What it shows:**
- Job data panel:
  - Last collection date
  - Number of active postings
  - Number of inactive/expired postings
  - Sources contributing to current data
  - Next scheduled collection (Phase 3+)
- Curriculum data panel:
  - Last update date
  - Number of programs and courses
  - Any programs with missing or very short descriptions (documentation risk list)
- Alignment pipeline panel:
  - Last run date
  - Run ID / version
  - Which data snapshot was used
  - Status: current / stale / running
- For Phase 1 MVP: this page shows static metadata — "Based on data collected March 2026. Automated refresh not yet implemented."

---

## Navigation and UX principles

1. **Every page has a clear "what this means" layer** — not just data, but interpretation
2. **Scores are always accompanied by context** — what the scale means, what a typical score looks like
3. **No research vocabulary in the main flow** — words like "experiment", "TF-IDF", "KeyBERT", "ESCO" belong only in the Evidence page
4. **Constructive framing throughout** — "strong foundations in X" before "gaps in Y"
5. **Clear distinction between what is certain and what is inferred** — especially for gap type labels
6. **Downloadable outputs** — curriculum committee members need to take data into meeting documents

---

## YSU-first filtering

For Phase 1, the product defaults to YSU and shows only YSU programs. The university selector is not shown. The header says "Yerevan State University."

When multi-university mode is added (Phase 2), the university selector appears after login and determines which programs are visible. Data is not separated by university at the file level — it is filtered at the query layer.
