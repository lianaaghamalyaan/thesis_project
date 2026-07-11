from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_alignment, load_curriculum, load_gaps, load_run_metadata, job_skills_coverage
from src.formatting import format_score, score_color, score_label, score_badge
from src.freshness import render_freshness_banner
from src.auth_ui import current_university


def _render():
    alignment = load_alignment()
    curriculum = load_curriculum()
    gaps = load_gaps()
    meta = load_run_metadata()

    st.title("Curriculum–Labor Market Alignment")
    st.markdown(f"**{current_university()}** · Program portfolio overview")
    st.caption(
        f"{meta['curriculum_snapshot']['n_programs']} programs · "
        f"{meta['curriculum_snapshot']['n_courses']:,} courses"
    )
    render_freshness_banner(meta)

    cov = job_skills_coverage()
    if cov["n_missing"] > 0:
        st.caption(
            f"ℹ️ Skill-level demand data (Strengths / Job Fit pages) covers {cov['n_covered']} of "
            f"{cov['n_total']} postings ({cov['n_missing']} newer postings pending skill extraction — "
            "run `pipeline/extract_job_skills.py` to fill the gap)."
        )

    # ── Key metrics ──────────────────────────────────────────────────────────
    mapped = alignment.dropna(subset=["core_role_coverage_pct"])
    mean_score = mapped["core_role_coverage_pct"].mean()
    n_programs = len(alignment)
    n_courses = len(curriculum)
    n_gap_skills = gaps["gap_skill"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Programs", n_programs)
    with c2:
        st.metric("Courses", f"{n_courses:,}")
    with c3:
        st.metric("Mean alignment score", f"{mean_score:.1f}%")
    with c4:
        st.metric("Unique gap skills identified", n_gap_skills)

    st.markdown("---")

    # ── Score context ─────────────────────────────────────────────────────────
    with st.expander("ℹ️  How to read alignment scores", expanded=False):
        st.markdown(
            """
**Alignment score** = percentage of skills commonly required in relevant IT job postings that a program's courses cover.

| Score | Meaning |
|---|---|
| 50%+ | **Strong** — program covers over half the role-relevant market skills |
| 35–50% | **Good** — solid coverage with targeted gaps |
| 25–35% | **Moderate** — clear opportunities to strengthen alignment |
| Below 25% | **Developing** — significant gaps or documentation issues likely |

A lower score does not always mean the program is weak — it may reflect vague or incomplete course descriptions
rather than a true curriculum gap. See the **Program Detail** page for a breakdown.
            """
        )

    # ── Program bar chart ────────────────────────────────────────────────────
    st.subheader("All Programs — Alignment Scores")

    chart_df = alignment.copy()
    chart_df = chart_df[chart_df["core_role_coverage_pct"].notna()].copy()
    chart_df["label"] = chart_df["program"] + " (" + chart_df["degree"] + ")"
    chart_df["color_band"] = chart_df["core_role_coverage_pct"].apply(score_label)
    chart_df = chart_df.sort_values("core_role_coverage_pct", ascending=True)

    color_map = {
        "Strong": "#2e7d32",
        "Good": "#558b2f",
        "Moderate": "#f57c00",
        "Developing": "#c62828",
        "No data": "#9e9e9e",
    }

    fig = px.bar(
        chart_df,
        x="core_role_coverage_pct",
        y="label",
        color="color_band",
        color_discrete_map=color_map,
        orientation="h",
        text="core_role_coverage_pct",
        labels={"core_role_coverage_pct": "Core role-aware coverage (%)", "label": ""},
        hover_data={"relevant_roles": True, "degree": False, "color_band": False},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=max(480, 32 * len(chart_df)),
        showlegend=True,
        legend_title="Score band",
        xaxis_range=[0, max(chart_df["core_role_coverage_pct"].max() * 1.15, 20)],
        margin=dict(l=10, r=40, t=10, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Handle unmapped programs
    unmapped = alignment[alignment["relevant_roles"].fillna("") == "unmapped"]
    if not unmapped.empty:
        st.caption(
            f"ℹ️  {', '.join(unmapped['program'] + ' (' + unmapped['degree'] + ')')} "
            f"{'is' if len(unmapped)==1 else 'are'} not mapped to specific role groups and "
            f"{'is' if len(unmapped)==1 else 'are'} excluded from the chart."
        )

    st.markdown("---")

    # ── Spotlight ─────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🌟 Strongest programs")
        top3 = chart_df.sort_values("core_role_coverage_pct", ascending=False).head(3)
        for _, row in top3.iterrows():
            st.markdown(
                f"**{row['program']}** ({row['degree']})  \n"
                f"{format_score(row['core_role_coverage_pct'])} · {row.get('relevant_roles', '')}"
            )
            st.progress(min(row["core_role_coverage_pct"] / 100, 1.0))

    with col_right:
        st.subheader("🔍 Most common gap skills")
        top_gaps = (
            gaps.groupby("gap_skill")["job_frequency"]
            .sum()
            .nlargest(8)
            .reset_index()
            .sort_values("job_frequency", ascending=True)
        )
        if not top_gaps.empty:
            fig2 = px.bar(
                top_gaps,
                x="job_frequency",
                y="gap_skill",
                orientation="h",
                labels={"job_frequency": "Job postings requiring this skill", "gap_skill": ""},
            )
            fig2.update_layout(height=280, margin=dict(l=10, r=20, t=10, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.info(
        "👉 Click **Programs** in the sidebar to explore individual programs, "
        "or go to **Program Detail** to see a deep breakdown of any program."
    )


_render()
