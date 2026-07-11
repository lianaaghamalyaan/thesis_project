from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import (
    load_alignment,
    load_confidence_tiers,
    load_curriculum,
    load_gaps,
    load_llm_gaps,
)
from src.doc_gap import compute_program_doc_score
from src.recs import get_cross_program_gaps
from src.formatting import format_score, score_color, score_label
from src.auth_ui import current_university


def _render():
    alignment = load_alignment()
    curriculum = load_curriculum()
    gaps = load_gaps()
    llm_gaps = load_llm_gaps()
    tiers = load_confidence_tiers()

    st.title("Recommendations")
    st.markdown(
        f"University-wide view of the most impactful improvement opportunities "
        f"across all {current_university()} IT programs."
    )

    # ── Priority matrix ──────────────────────────────────────────────────────
    st.subheader("Priority matrix: effort vs. impact")

    with st.container(border=True):
        col_doc, col_curr = st.columns(2)

        with col_doc:
            st.markdown("#### 📝 Documentation improvements")
            st.caption("Lower effort · Improves measured alignment without curriculum changes")

            doc_scores = []
            for _, row in alignment.iterrows():
                doc_score = compute_program_doc_score(row["program"], row["degree"], curriculum, tiers)
                doc_scores.append({
                    "program": row["program"],
                    "degree": row["degree"],
                    "score": row.get("core_role_coverage_pct"),
                    "doc_score": doc_score,
                })

            doc_df = pd.DataFrame(doc_scores)
            weak_doc = doc_df[doc_df["doc_score"] < 0.30].sort_values("doc_score")

            if weak_doc.empty:
                st.success("All programs have reasonable documentation quality.")
            else:
                st.markdown(
                    f"**{len(weak_doc)} program{'s' if len(weak_doc)!=1 else ''} with weak course descriptions:**"
                )
                for _, drow in weak_doc.iterrows():
                    st.markdown(
                        f"— **{drow['program']}** ({drow['degree']})  \n"
                        f"  Documentation quality: {drow['doc_score']:.0%} · "
                        f"Alignment score: {format_score(drow['score'])}"
                    )

        with col_curr:
            st.markdown("#### 📖 Curriculum content gaps")
            st.caption("Higher effort · Requires adding or updating course content")

            # Programs with strong documentation but low score — likely real curriculum gaps
            well_doc = doc_df[(doc_df["doc_score"] >= 0.40) & (doc_df["score"].notna()) & (doc_df["score"] < 35)]
            if well_doc.empty:
                st.info("No programs with both strong documentation and low alignment scores detected.")
            else:
                st.markdown(
                    f"**{len(well_doc)} program{'s' if len(well_doc)!=1 else ''} with well-documented courses but low alignment:**"
                )
                for _, drow in well_doc.iterrows():
                    st.markdown(
                        f"— **{drow['program']}** ({drow['degree']})  \n"
                        f"  Alignment: {format_score(drow['score'])} · "
                        f"Documentation: {drow['doc_score']:.0%}"
                    )
                st.caption("These programs' gaps are more likely to reflect real curriculum content gaps.")

    st.markdown("---")

    # ── Cross-program gap skills ───────────────────────────────────────────
    st.subheader("Skills missing across the most programs")
    st.caption("These skills are absent from multiple programs — addressing them would have the broadest impact.")

    cross_gaps = get_cross_program_gaps(gaps)
    if not cross_gaps.empty:
        fig = px.bar(
            cross_gaps.head(20).sort_values("n_programs"),
            x="n_programs",
            y="gap_skill",
            orientation="h",
            color="total_frequency",
            color_continuous_scale="Oranges",
            text="n_programs",
            labels={
                "n_programs": "Programs missing this skill",
                "gap_skill": "",
                "total_frequency": "Total job mentions",
            },
        )
        fig.update_traces(texttemplate="%{text} programs", textposition="outside")
        fig.update_layout(height=520, margin=dict(l=10, r=40, t=10, b=20))
        fig.update_coloraxes(colorbar_title="Job mentions")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Category breakdown ────────────────────────────────────────────────
    if "category" in llm_gaps.columns:
        st.subheader("Gaps by category")
        cat_summary = (
            llm_gaps.groupby("category")
            .agg(n_gaps=("missing_skill", "count"), total_freq=("job_frequency", "sum"))
            .reset_index()
            .sort_values("total_freq", ascending=False)
        )
        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.pie(
                cat_summary,
                names="category",
                values="n_gaps",
                title="Gap count by category",
                hole=0.4,
            )
            fig2.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = px.bar(
                cat_summary.sort_values("total_freq"),
                x="total_freq",
                y="category",
                orientation="h",
                text="total_freq",
                labels={"total_freq": "Total job mentions", "category": ""},
                title="Gap urgency by category",
            )
            fig3.update_traces(textposition="outside")
            fig3.update_layout(height=340, margin=dict(l=10, r=40, t=40, b=10))
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Program-level table ────────────────────────────────────────────────
    st.subheader("All programs — alignment at a glance")

    doc_df_indexed = doc_df.set_index(["program", "degree"])
    display_rows = []
    for _, arow in alignment.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows():
        key = (arow["program"], arow["degree"])
        d_score = doc_df_indexed.loc[key, "doc_score"] if key in doc_df_indexed.index else None
        display_rows.append({
            "Program": arow["program"],
            "Degree": arow["degree"],
            "Alignment": format_score(arow.get("core_role_coverage_pct")),
            "Band": score_label(arow.get("core_role_coverage_pct")),
            "Doc. quality": f"{d_score:.0%}" if d_score is not None else "—",
            "Gap count": int(arow.get("core_n_gap", 0)) if pd.notna(arow.get("core_n_gap")) else "—",
        })

    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Alignment": st.column_config.TextColumn("Alignment"),
            "Band": st.column_config.TextColumn("Band"),
        },
    )


_render()
