from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.data_loader import load_curriculum, load_gaps, load_run_metadata, load_alignment, load_confidence_tiers
from src.doc_gap import compute_program_doc_score
from src.auth_ui import current_university


def _render():
    meta = load_run_metadata()
    curriculum = load_curriculum()
    gaps = load_gaps()
    alignment = load_alignment()
    tiers = load_confidence_tiers()

    st.title("Data & Admin")
    st.markdown("Data freshness, pipeline status, and documentation quality across programs.")

    # ── Data freshness status ─────────────────────────────────────────────
    st.subheader("📅 Data freshness")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Job market data**")
            st.markdown(
                f"- Status: 🟡 **Static snapshot** (not yet automated)  \n"
                f"- Last collected: **{meta['job_snapshot']['collected_at']}**  \n"
                f"- IT postings: **{meta['job_snapshot']['n_it_postings']:,}**  \n"
                f"- Sources: **{meta['job_snapshot']['n_sources']}**  \n"
            )
        with col2:
            st.markdown("**Curriculum data**")
            st.markdown(
                f"- Status: 🟡 **Static snapshot** (not yet automated)  \n"
                f"- Last collected: **{meta['curriculum_snapshot']['collected_at']}**  \n"
                f"- Courses: **{meta['curriculum_snapshot']['n_courses']:,}**  \n"
                f"- Programs: **{meta['curriculum_snapshot']['n_programs']}**  \n"
            )

    st.info(
        "ℹ️ This is Phase 1 (static). Automated job collection and scheduled pipeline runs "
        "are planned for Phase 3. See the roadmap in the project documentation."
    )

    st.markdown("---")

    # ── Pipeline run ──────────────────────────────────────────────────────
    st.subheader("⚙️ Analysis pipeline")

    with st.container(border=True):
        st.markdown(
            f"**Run ID:** `{meta['run_id']}`  \n"
            f"**Analysis date:** {meta['created_at']}  \n"
            f"**Experiment:** `{meta['experiment']}`  \n"
            f"**ESCO version:** {meta['esco_version']}  \n"
            f"**Notes:** {meta.get('notes', '—')}"
        )

    st.markdown("---")

    # ── Documentation quality by program ─────────────────────────────────
    st.subheader("📝 Documentation quality by program")
    st.caption(
        "Programs with low documentation quality may show lower alignment scores due to incomplete course descriptions, "
        "not necessarily due to curriculum content gaps."
    )

    rows = []
    for _, arow in alignment.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows():
        doc_score = compute_program_doc_score(arow["program"], arow["degree"], curriculum, tiers)
        n_courses = len(curriculum[
            (curriculum["program_name"] == arow["program"]) &
            (curriculum["degree_level"] == arow["degree"])
        ])
        flag = "⚠️" if doc_score < 0.25 else ("🟡" if doc_score < 0.40 else "✅")
        rows.append({
            "Program": arow["program"],
            "Degree": arow["degree"],
            "Courses": n_courses,
            "Doc. quality": f"{doc_score:.0%}",
            "Status": flag,
        })

    import pandas as pd
    doc_df = pd.DataFrame(rows)
    st.dataframe(doc_df, use_container_width=True, hide_index=True)

    st.markdown(
        "✅ Good documentation (≥40%) · 🟡 Mixed (25–40%) · ⚠️ Weak (<25%)"
    )

    st.markdown("---")

    # ── Programs missing descriptions ─────────────────────────────────────
    missing_desc = curriculum[curriculum["description"].isna() | (curriculum["description"].str.len() < 50)]
    if not missing_desc.empty:
        st.subheader("⚠️ Courses with missing or very short descriptions")
        st.caption(
            f"{len(missing_desc)} courses have no description or descriptions under 50 characters. "
            "These courses cannot be analyzed for skill alignment."
        )
        st.dataframe(
            missing_desc[["program_name", "degree_level", "course_name", "description"]].head(30),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.caption(f"CurriculumLens · {current_university()} · Data: March 2026")


_render()
