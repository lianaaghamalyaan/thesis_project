from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.auth_ui import can_switch_university
from src.benchmark import load_all_universities_alignment
from src.formatting import format_score, score_color, score_label


def _render():
    if not can_switch_university():
        st.error("This view is only available to policy and platform-operator accounts.")
        st.stop()

    st.title("All Universities — National Overview")
    st.caption(
        "Every program on the platform, named. Visible to policy and platform-operator "
        "accounts only — university accounts see anonymized peer comparisons instead "
        "(Program Detail → How this compares)."
    )

    alignment = load_all_universities_alignment()
    scored = alignment[alignment["core_role_coverage_pct"].notna()].copy()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Universities", scored["university"].nunique())
    with c2:
        st.metric("Programs", len(scored))
    with c3:
        st.metric("National mean alignment", f"{scored['core_role_coverage_pct'].mean():.1f}%")

    st.markdown("---")

    # ── University-level comparison ─────────────────────────────────────────
    st.subheader("By university")
    uni_summary = (
        scored.groupby("university")
        .agg(
            n_programs=("program", "count"),
            mean_score=("core_role_coverage_pct", "mean"),
            max_score=("core_role_coverage_pct", "max"),
        )
        .reset_index()
        .sort_values("mean_score", ascending=False)
    )
    fig = px.bar(
        uni_summary,
        x="mean_score",
        y="university",
        orientation="h",
        text="mean_score",
        labels={"mean_score": "Mean core role-aware coverage (%)", "university": ""},
        hover_data={"n_programs": True, "max_score": ":.1f"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=max(320, 40 * len(uni_summary)), margin=dict(l=10, r=40, t=10, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Program-level table, all universities ───────────────────────────────
    st.subheader("All programs, all universities")

    c1, c2 = st.columns([1, 2])
    with c1:
        uni_filter = st.selectbox("Filter by university", ["All"] + sorted(scored["university"].unique().tolist()))
    with c2:
        query = st.text_input("Search by program name", placeholder="e.g. Data Science")

    filtered = scored.copy()
    if uni_filter != "All":
        filtered = filtered[filtered["university"] == uni_filter]
    if query:
        filtered = filtered[filtered["program"].str.contains(query, case=False, na=False)]
    filtered = filtered.sort_values("core_role_coverage_pct", ascending=False)

    st.dataframe(
        filtered[["university", "program", "degree", "relevant_roles", "core_role_coverage_pct", "core_n_gap"]].rename(
            columns={
                "university": "University",
                "program": "Program",
                "degree": "Degree",
                "relevant_roles": "Relevant roles",
                "core_role_coverage_pct": "Alignment (%)",
                "core_n_gap": "Gaps",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


_render()
