"""
YSU Administration Report — Full Results for All Programs.

A structured, printable-quality overview of alignment results for all 13 mapped YSU IT programs,
intended for review by academic leadership, curriculum committees, and prospective institutional partners.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import (
    load_alignment,
    load_confidence_tiers,
    load_course_skills,
    load_curriculum,
    load_gaps,
    load_job_skills_by_role,
    load_llm_gaps,
    load_run_metadata,
)
from src.alignment import get_program_skills, get_role_skill_counter, expand_roles
from src.doc_gap import compute_program_doc_score
from src.formatting import format_score, score_color, score_label, CATEGORY_ICONS

# ── Data ────────────────────────────────────────────────────────────────────
alignment = load_alignment()
curriculum = load_curriculum()
gaps = load_gaps()
llm_gaps = load_llm_gaps()
course_skills = load_course_skills()
tiers = load_confidence_tiers()
job_skills_by_role = load_job_skills_by_role()
meta = load_run_metadata()

# Programs in presentation order (slide 19 of defense)
PROGRAM_ORDER = [
    ("Data Science in Business", "Master"),
    ("Applied Statistics and Data Science", "Master"),
    ("Applied Statistics and Data Science", "Bachelor"),
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"),
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"),
    ("Information Systems Management", "Master"),
    ("Information Systems Development", "Master"),
    ("Information Security", "Bachelor"),
    ("Discrete Mathematics and Theoretical Informatics", "Master"),
    ("Numerical Analysis and Mathematical Modelling", "Master"),
    ("Radiophysics and Computer Technology", "Bachelor"),
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"),
    ("Informatics and Applied Mathematics", "Bachelor"),
]

# Faculty mapping (from slide 19)
FACULTY_MAP = {
    ("Data Science in Business", "Master"): "Faculty of Economics & Management",
    ("Applied Statistics and Data Science", "Master"): "Faculty of Mathematics & Mechanics",
    ("Applied Statistics and Data Science", "Bachelor"): "Faculty of Mathematics & Mechanics",
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"): "Faculty of Physics",
    ("Information Systems Management", "Master"): "IT Educational & Research Center",
    ("Information Systems Development", "Master"): "IT Educational & Research Center",
    ("Information Security", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
    ("Discrete Mathematics and Theoretical Informatics", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Numerical Analysis and Mathematical Modelling", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Radiophysics and Computer Technology", "Bachelor"): "Faculty of Radiophysics",
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
    ("Informatics and Applied Mathematics", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
}

# Specific interpretive notes per program (domain knowledge)
PROGRAM_NOTES = {
    ("Data Science in Business", "Master"): (
        "**Note on skill detection:** Several tools (Apache Spark, Docker, Git workflows, "
        "CI/CD practices) are partially introduced in this program but are not explicitly "
        "mentioned in the published course syllabi. They therefore appear in the 'missing' "
        "list below. This is a documentation gap, not necessarily a curriculum gap. "
        "Collecting what is actually delivered in lectures would likely move these tools "
        "into the 'matched' column."
    ),
    ("Applied Statistics and Data Science", "Master"): (
        "**Strong analytical foundation.** This program's statistical and modelling depth "
        "maps well onto market demand in data roles. Gaps concentrate in applied production "
        "tools (cloud platforms, MLOps, deployment frameworks) — a natural and low-risk "
        "area for targeted elective additions."
    ),
    ("Applied Statistics and Data Science", "Bachelor"): (
        "**Broad mathematical coverage.** The undergraduate track teaches a wide range "
        "of statistical and computational methods. Like the master's, the gap concentrates "
        "in applied tooling. The high surplus reflects the depth of theoretical content "
        "that the market does not explicitly list but that forms graduate capacity."
    ),
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"): (
        "**Strong software and systems coverage.** This program is compared against "
        "Software Engineering and DevOps / Cloud roles, where it performs above the YSU "
        "average. The existing systems-level curriculum aligns well with software engineering "
        "demand; DevOps production tooling is the main gap."
    ),
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"): (
        "**Physics-rooted data curriculum.** This program covers substantial mathematical "
        "and AI theory grounded in physics applications. Many skills listed as surplus are "
        "domain-specific physics methods that fall outside standard IT job descriptions — "
        "they represent academic depth, not wasted content."
    ),
    ("Information Systems Management", "Master"): (
        "**Systems and management focus.** Compared against IT support and technical "
        "management roles. The score reflects solid coverage of enterprise systems concepts. "
        "Gaps lie in modern cloud administration tooling and scripting automation "
        "increasingly expected in IT management roles."
    ),
    ("Information Systems Development", "Master"): (
        "**Development-oriented systems program.** Covers software engineering and IT systems "
        "tracks. Gaps are primarily in modern web frameworks, cloud infrastructure, and "
        "DevOps practices. The program's software development foundations are market-relevant."
    ),
    ("Information Security", "Bachelor"): (
        "**Security is a specialized, high-demand domain.** The market for security roles "
        "is smaller but the skill requirements are deep and specific. This program covers "
        "strong theoretical and cryptographic foundations. Gaps include modern cloud security, "
        "containerized environments, and specific offensive/defensive tooling increasingly "
        "listed in job postings."
    ),
    ("Discrete Mathematics and Theoretical Informatics", "Master"): (
        "**Theory-heavy program by design.** This program is deliberately foundational — "
        "formal methods, computation theory, algorithm theory. Its lower alignment score "
        "reflects the distance between theoretical informatics and job-market applied tools, "
        "not a program failure. Graduates from this track typically have strong abstract "
        "reasoning capacity that underpins advanced technical roles."
    ),
    ("Numerical Analysis and Mathematical Modelling", "Master"): (
        "**Computational mathematics focus.** Strong alignment with the mathematical side "
        "of data and software roles. Similar pattern to Discrete Mathematics: deep theory, "
        "limited applied tooling documentation. The modelling skills are genuinely valuable "
        "even when not explicitly listed in job descriptions."
    ),
    ("Radiophysics and Computer Technology", "Bachelor"): (
        "**Hardware and embedded systems.** This program is compared against Hardware / "
        "Embedded roles — a specialized and smaller market segment in Armenia. The high "
        "surplus count reflects physics and electronics content not captured in current "
        "IT job postings. The program's embedded systems and hardware foundations are real "
        "and valuable; the market simply does not frequently list them as keywords."
    ),
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"): (
        "**General informatics — compared across all role groups.** This broad program is "
        "compared against the entire IT market (all role groups), which makes the denominator "
        "very large. The lower percentage reflects breadth rather than weakness: the program "
        "covers foundational content across many areas without specializing deeply in any one "
        "market category. This is by design for a broad bachelor's track."
    ),
    ("Informatics and Applied Mathematics", "Bachelor"): (
        "**Same as Part-time track above** — broad informatics compared against all IT roles. "
        "The full-time and part-time tracks have near-identical scores because their curricula "
        "are similar. The observation about breadth vs. specialization applies equally here."
    ),
}


def get_matched_skills(program, degree, relevant_roles, n=30):
    """Skills the program covers that appear in job market demand."""
    prog_skills = get_program_skills(program, degree, curriculum, course_skills)
    role_counter = get_role_skill_counter(relevant_roles, job_skills_by_role)
    matched = [
        {"skill": s, "count": role_counter[s]}
        for s in prog_skills
        if s in role_counter
    ]
    matched.sort(key=lambda x: -x["count"])
    return matched[:n]


def get_surplus_skill_names(program, degree, relevant_roles, n=25):
    """Skills the program covers that do NOT appear in job market demand for its roles."""
    prog_skills = get_program_skills(program, degree, curriculum, course_skills)
    role_counter = get_role_skill_counter(relevant_roles, job_skills_by_role)
    surplus = sorted(prog_skills - set(role_counter.keys()))
    return surplus[:n]


def get_missing_skills_with_categories(program, degree, n=25):
    """Get missing skills from llm_gap_analysis with categories, fallback to gap_analysis."""
    prog_llm = llm_gaps[
        (llm_gaps["program_name"] == program) & (llm_gaps["degree_level"] == degree)
    ].sort_values("job_frequency", ascending=False)

    if not prog_llm.empty:
        return prog_llm.head(n)[["missing_skill", "job_frequency", "category"]].to_dict("records")

    prog_gaps = gaps[
        (gaps["program"] == program) & (gaps["degree"] == degree)
    ].sort_values("job_frequency", ascending=False)
    return [{"missing_skill": r["gap_skill"], "job_frequency": r["job_frequency"], "category": "—"}
            for _, r in prog_gaps.head(n).iterrows()]


# ── Report rendering ────────────────────────────────────────────────────────

def render_report():
    # ── Cover ────────────────────────────────────────────────────────────────
    st.markdown(
        """
<div style="text-align:center;padding:40px 20px 20px;border-bottom:3px solid #1a1a2e">
<div style="font-size:0.9em;color:#555;letter-spacing:2px;text-transform:uppercase">Yerevan State University</div>
<h1 style="font-size:2em;margin:10px 0;color:#1a1a2e">IT Curriculum — Labor Market Alignment</h1>
<h2 style="font-size:1.3em;font-weight:400;color:#444;margin:0">Program-by-Program Results Report</h2>
<div style="margin-top:16px;font-size:0.9em;color:#666">
Prepared by: Liana Aghamalyan · MSc in Data Science for Business · 2026<br>
Based on 650 Armenian IT job postings · 697 YSU courses · 13 mapped programs<br>
Data snapshot: March 2026 · Method: LLM skill extraction + ESCO v1.2 semantic matching
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("&nbsp;")

    # ── Executive summary ────────────────────────────────────────────────────
    st.header("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)
    ysu_mapped = alignment.dropna(subset=["core_role_coverage_pct"])
    mean_score = ysu_mapped["core_role_coverage_pct"].mean()

    with col1:
        st.metric("Programs analyzed", "14 total · 13 mapped")
    with col2:
        st.metric("Mean alignment score", f"{mean_score:.1f}%")
    with col3:
        st.metric("National average", "24.1%")
    with col4:
        st.metric("YSU vs. national", f"+{mean_score - 24.1:.1f} pp")

    st.markdown(
        f"""
YSU's IT programs achieve a mean role-aware alignment score of **{mean_score:.1f}%**,
slightly above the national average across 8 Armenian universities (**24.1%**).
The strongest program — **Data Science in Business (Master's)** — reaches **62.5%**,
ranking second nationally. Thirteen programs were mapped to specific ESCO job-market role groups;
one program (Blockchain and Digital Currencies) lacked sufficient job-market data for mapping.

**What alignment measures.** The score indicates what percentage of the skills explicitly required
by employers in relevant IT job postings are covered by a program's published course syllabi.
A score of 30% means the program documents coverage of roughly 30 out of every 100 skills
that employers in its target roles list. This is a lower bound — skills that are taught but
not documented in syllabi are not counted.

**Why scores are not low.** A score of 20–30% is not a failure. No single program is expected
to cover every employer skill. The market demands thousands of skills across all levels and
specializations; programs rightly focus on deep foundations. The national range is 2–63%,
and YSU's specialized master's programs cluster in the upper half.
""",
    )

    st.markdown("---")

    # ── Portfolio chart ─────────────────────────────────────────────────────
    st.header("Program Portfolio — All Programs Ranked")

    ordered_rows = []
    for prog, deg in PROGRAM_ORDER:
        row = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
        if not row.empty:
            r = row.iloc[0]
            ordered_rows.append({
                "label": f"{prog} ({deg})",
                "score": r.get("core_role_coverage_pct"),
                "band": score_label(r.get("core_role_coverage_pct")),
                "roles": str(r.get("relevant_roles", "")),
            })

    chart_df = pd.DataFrame(ordered_rows)
    chart_df = chart_df[chart_df["score"].notna()]
    chart_df = chart_df.sort_values("score", ascending=True)

    color_map = {
        "Strong": "#2e7d32",
        "Good": "#558b2f",
        "Moderate": "#f57c00",
        "Developing": "#c62828",
    }

    # National average reference line
    fig = px.bar(
        chart_df,
        x="score",
        y="label",
        color="band",
        color_discrete_map=color_map,
        orientation="h",
        text="score",
        labels={"score": "Core role-aware coverage (%)", "label": "", "band": "Band"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.add_vline(
        x=26.5,
        line_dash="dash",
        line_color="#1565c0",
        annotation_text="YSU mean 26.5%",
        annotation_position="top right",
        annotation_font_color="#1565c0",
    )
    fig.add_vline(
        x=24.1,
        line_dash="dot",
        line_color="#9e9e9e",
        annotation_text="National avg 24.1%",
        annotation_position="bottom right",
        annotation_font_color="#9e9e9e",
    )
    fig.update_layout(
        height=max(500, 38 * len(chart_df)),
        xaxis_range=[0, max(chart_df["score"].max() * 1.15, 30)],
        margin=dict(l=10, r=60, t=20, b=20),
        showlegend=True,
        legend_title="Score band",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Important context ────────────────────────────────────────────────────
    st.header("How to Read These Results")

    with st.container(border=True):
        st.markdown("""
**The three skill categories** — used throughout this report:

| Category | What it means | What it implies |
|---|---|---|
| ✅ **Matched** | Skills the program covers that employers in its target roles actively require | These are curriculum strengths — the program is delivering market-relevant content |
| ⚠️ **Missing** | Skills employers actively require that are NOT found in the program's published syllabi | Primary target for improvement — but distinguish documentation gaps from real gaps (see below) |
| ◦ **Surplus** | Skills the program covers that employers do not explicitly list in job postings | **Not waste.** These are typically mathematical foundations, theoretical methods, and academic depth — real value that underpins graduate capability but does not appear as a keyword in job postings |

**Documentation gap vs. curriculum gap — the most important distinction:**

Not every skill in the "missing" column is genuinely absent from the curriculum.
Many programs teach tools and practices in lectures that never make it into the published online syllabus.
When a skill appears in the "missing" list, there are two possible explanations:

1. **Real curriculum gap** — the skill is genuinely not taught. This requires adding content.
2. **Documentation gap** — the skill is taught but the published description does not mention it. This can be fixed by updating course descriptions — a low-cost, high-impact first step.

For YSU specifically, the analysis in Slide 21 of the defense presentation notes:
*"Unlike most universities in this study, YSU publishes full, real course descriptions for all 14 programs.
So YSU's coverage is not an estimate or an under-count — it reflects what the curriculum actually documents."*

The one refinement left is lecture-level detail. A precise, low-cost first step:
ask professors what they actually deliver beyond the online syllabus.
The "missing" list then divides into what genuinely needs adding and what only needs documenting.

**Alignment scores reflect the published syllabi as of March 2026.**
""")

    st.markdown("---")

    # ── Per-program sections ──────────────────────────────────────────────────
    st.header("Program-by-Program Analysis")

    for prog, deg in PROGRAM_ORDER:
        _render_program(prog, deg)

    # ── Unmapped programs ─────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Blockchain and Digital Currencies (Master's) — Not mapped")
    with st.container(border=True):
        st.markdown(
            """
This program could not be assigned to a standard ESCO IT role group because
blockchain and digital currency roles are not yet well-represented in the ESCO taxonomy
and the available Armenian job postings for this specialization were too few for a reliable comparison.
The program has 15 courses. A meaningful alignment score would require a dedicated job-market
corpus for blockchain/fintech roles, which was outside the scope of this study.
"""
        )

    st.markdown("---")

    # ── Closing ───────────────────────────────────────────────────────────────
    st.header("Summary and Recommendations")

    st.markdown(
        f"""
**Key findings from this analysis:**

1. **YSU specialised master's programs lead nationally.** Data Science in Business (62.5%)
and Applied Statistics & Data Science (40.6%) rank among the strongest programs in the full
8-university dataset of 40 mapped programs.

2. **The structural gap is in applied production tooling.** Docker, Kubernetes, cloud platforms
(AWS/Azure/GCP), CI/CD, and MLOps are present across every program's missing list.
This is a national-level structural pattern, not a YSU-specific failure.

3. **Theoretical foundations are a genuine strength.** Mathematics, statistics, algorithms,
and programming fundamentals are well-covered. The surplus column reflects this depth —
the programs teach more theory than employers explicitly list, and that is appropriate.

4. **Documentation quality is YSU's differentiator.** YSU is the only university in this study
where full course descriptions are publicly available. This means YSU's scores are real
measurements, not under-counts caused by missing data.

5. **The quickest win is documentation-level.** Before any curriculum revision,
collecting what professors actually deliver in lectures would give a more accurate picture
and would likely raise measured alignment for many programs.

**Suggested next steps:**

- Identify 2–3 programs and ask faculty to document actual lecture content beyond the online syllabus
- Consider optional elective modules around cloud/DevOps/MLOps tooling in the strongest data programs
- Re-run this analysis with updated descriptions to see the effect before committing to curriculum changes
- Use this dashboard for ongoing annual review as job market data is refreshed

*This report is based on automated NLP analysis of published course descriptions and Armenian IT job postings
from March 2026. It is intended as a decision-support input, not a prescriptive audit.*

---
**Data snapshot:** {meta['job_snapshot']['n_it_postings']:,} IT job postings from {meta['job_snapshot']['n_sources']} sources ·
{meta['curriculum_snapshot']['n_courses']:,} courses ·
Collected: {meta['job_snapshot']['collected_at']} ·
Method: `{meta['experiment']}` · ESCO {meta['esco_version']}
"""
    )


def _render_program(program, degree):
    """Render a single program section."""
    row = alignment[(alignment["program"] == program) & (alignment["degree"] == degree)]
    if row.empty:
        return
    r = row.iloc[0]

    score = r.get("core_role_coverage_pct")
    n_matched = int(r.get("core_n_overlap", 0)) if pd.notna(r.get("core_n_overlap")) else "?"
    n_job_skills = int(r.get("core_n_job_skills", 0)) if pd.notna(r.get("core_n_job_skills")) else "?"
    n_gaps = int(r.get("core_n_gap", 0)) if pd.notna(r.get("core_n_gap")) else "?"
    n_program_skills = int(r.get("n_program_skills", 0)) if pd.notna(r.get("n_program_skills")) else "?"
    n_surplus = int(r.get("n_surplus_clean", 0)) if pd.notna(r.get("n_surplus_clean")) else "?"
    relevant_roles = str(r.get("relevant_roles", ""))
    faculty = FACULTY_MAP.get((program, degree), "Yerevan State University")
    doc_score = compute_program_doc_score(program, degree, curriculum, tiers)
    color = score_color(score)
    label = score_label(score)

    st.markdown("---")

    # Program header
    st.markdown(
        f'<div style="background:#f8f9fa;border-left:6px solid {color};padding:16px 20px;border-radius:4px;margin-bottom:16px">'
        f'<div style="font-size:1.2em;font-weight:700;color:#1a1a2e">{program}</div>'
        f'<div style="color:#555;font-size:0.9em">{degree} · {faculty}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Score row
    col_score, col_meta, col_doc = st.columns([1, 2, 2])

    with col_score:
        st.markdown(
            f'<div style="text-align:center;padding:12px;background:#fff;border:2px solid {color};border-radius:8px">'
            f'<div style="font-size:2.2em;font-weight:800;color:{color}">{format_score(score)}</div>'
            f'<div style="font-size:0.85em;color:{color};font-weight:600">{label}</div>'
            f'<div style="font-size:0.75em;color:#777;margin-top:4px">core role-aware</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_meta:
        st.markdown(
            f"**Matched:** {n_matched} of {n_job_skills} role-relevant skills  \n"
            f"**Missing:** {n_gaps} skills demanded but not documented  \n"
            f"**Surplus:** {n_surplus} skills taught, not demanded by the market  \n"
            f"**Relevant roles:** {relevant_roles if relevant_roles not in ('unmapped','nan','') else 'General IT'}"
        )

    with col_doc:
        st.markdown(
            f"**Documentation quality:** {doc_score:.0%}  \n"
            f"*Proportion of extracted skills with high extraction confidence.*  \n"
            f"{'⚠️ Low documentation quality — some gaps may be documentation rather than curriculum gaps.' if doc_score < 0.30 else '✅ Reasonable documentation quality — gaps are more likely real curriculum gaps.' if doc_score >= 0.40 else '🟡 Mixed documentation quality — some gaps may be documentation gaps.'}"
        )

    # Specific program note
    note = PROGRAM_NOTES.get((program, degree))
    if note:
        with st.container(border=False):
            st.markdown(
                f'<div style="background:#fff8e1;border-left:4px solid #f9a825;padding:10px 14px;border-radius:4px;font-size:0.9em;margin:8px 0">'
                f"ℹ️ {note}"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Three-column skill breakdown
    col_match, col_miss, col_surplus = st.columns(3)

    with col_match:
        st.markdown("**✅ Matched skills**")
        st.caption("Program covers these, market requires them")
        matched = get_matched_skills(program, degree, relevant_roles, n=20)
        if matched:
            for item in matched[:15]:
                count_str = f" ({item['count']})" if item["count"] else ""
                st.markdown(f"✅ {item['skill']}{count_str}")
            if len(matched) > 15:
                st.caption(f"+ {len(matched) - 15} more")
        else:
            st.caption("No direct matches found in extracted skills.")

    with col_miss:
        st.markdown("**⚠️ Missing skills**")
        st.caption("Market requires these, not documented in program")
        missing = get_missing_skills_with_categories(program, degree, n=20)
        if missing:
            prev_cat = None
            for item in missing[:20]:
                cat = item.get("category", "—")
                if cat != prev_cat and cat != "—":
                    icon = CATEGORY_ICONS.get(cat, "🔹")
                    st.markdown(f"*{icon} {cat}*")
                    prev_cat = cat
                freq = item["job_frequency"]
                freq_str = f" ({int(freq)})" if pd.notna(freq) and freq else ""
                st.markdown(f"⚠️ {item['missing_skill']}{freq_str}")
        else:
            st.success("No significant gaps identified.")

    with col_surplus:
        st.markdown("**◦ Surplus skills**")
        st.caption("Program teaches these; not in job postings — valuable academic foundations")
        surplus = get_surplus_skill_names(program, degree, relevant_roles, n=15)
        if surplus:
            for s in surplus[:15]:
                st.markdown(f"◦ {s}")
            rem = n_surplus - len(surplus) if isinstance(n_surplus, int) else 0
            if rem > 0:
                st.caption(f"+ approximately {rem} more academic foundations not listed in job postings")
        else:
            st.caption("Surplus skills not computable for this program.")


render_report()
