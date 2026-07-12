from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
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
from src.alignment import get_strengths
from src.benchmark import render_benchmark_panel
from src.doc_gap import compute_program_doc_score
from src.formatting import (
    CATEGORY_ICONS,
    GAP_TYPE_ICONS,
    GAP_TYPE_LABELS,
    format_score,
    roles_display,
    score_color,
    score_interpretation,
    score_label,
)
from src.report import build_program_pdf
from src.auth_ui import current_university


def _program_selector(alignment):
    """Sidebar or top-of-page program selector. Respects session state,
    but only within the same university — switching university (via the
    admin banner) must not carry over a program selection that belongs to
    a different university's data, even if a same-named program happens
    to exist there too."""
    options = [
        (row["program"], row["degree"])
        for _, row in alignment.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows()
    ]
    labels = [f"{p} ({d})" for p, d in options]

    # Try to restore selection from session state (e.g. navigated from
    # Programs page) — but only if it was saved for the same university.
    default_idx = 0
    if st.session_state.get("selected_program_university") == current_university():
        saved_program = st.session_state.get("selected_program")
        saved_degree = st.session_state.get("selected_degree")
        if saved_program and saved_degree:
            for i, (p, d) in enumerate(options):
                if p == saved_program and d == saved_degree:
                    default_idx = i
                    break

    selected_label = st.selectbox(
        "Select a program",
        labels,
        index=default_idx,
        key="program_detail_selector",
    )
    idx = labels.index(selected_label)
    program, degree = options[idx]
    # Persist selection, tagged with the university it belongs to.
    st.session_state["selected_program"] = program
    st.session_state["selected_degree"] = degree
    st.session_state["selected_program_university"] = current_university()
    return program, degree


def _render():
    alignment = load_alignment()
    curriculum = load_curriculum()
    gaps = load_gaps()
    llm_gaps = load_llm_gaps()
    course_skills = load_course_skills()
    tiers = load_confidence_tiers()
    job_skills_by_role = load_job_skills_by_role()

    st.title("Program Detail")

    program, degree = _program_selector(alignment)

    row = alignment[
        (alignment["program"] == program) & (alignment["degree"] == degree)
    ]
    if row.empty:
        st.error("No alignment data found for this program.")
        return
    row = row.iloc[0]

    score = row.get("core_role_coverage_pct")
    relevant_roles = str(row.get("relevant_roles", ""))
    n_covered = int(row.get("core_n_overlap", 0)) if pd.notna(row.get("core_n_overlap")) else 0
    n_gap = int(row.get("core_n_gap", 0)) if pd.notna(row.get("core_n_gap")) else 0
    n_total = int(row.get("core_n_job_skills", 0)) if pd.notna(row.get("core_n_job_skills")) else 0

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(f"### {program}")
    st.caption(f"{degree} · {current_university()}")
    st.markdown("---")

    # ── Score panel ────────────────────────────────────────────────────────
    color = score_color(score)
    label = score_label(score)

    col_score, col_context = st.columns([1, 3])
    with col_score:
        st.markdown(
            f'<div style="text-align:center;padding:20px;background:#f8f9fa;border-radius:12px">'
            f'<div style="font-size:3em;font-weight:800;color:{color}">{format_score(score)}</div>'
            f'<div style="font-size:1em;color:{color};font-weight:600">{label}</div>'
            f'<div style="font-size:0.8em;color:#555;margin-top:6px">Core role-aware coverage</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_context:
        st.markdown(score_interpretation(score, relevant_roles))
        if n_total > 0:
            st.caption(
                f"Covers **{n_covered}** of **{n_total}** core role skills · "
                f"**{n_gap}** skills identified as gaps"
            )
        if relevant_roles and relevant_roles not in ("unmapped", "nan", ""):
            st.caption(f"📌 Relevant roles: {roles_display(relevant_roles)}")

    st.markdown("---")
    benchmark = render_benchmark_panel(score, current_university(), degree, relevant_roles)

    # ── Coverage breakdown (secondary metrics) ─────────────────────────────
    with st.expander("📊 Full coverage breakdown", expanded=False):
        metrics = {
            "Full market coverage": row.get("full_coverage_pct"),
            "Role-aware coverage": row.get("role_coverage_pct"),
            "Core role-aware coverage": row.get("core_role_coverage_pct"),
            "Weighted core coverage": row.get("weighted_core_coverage_pct"),
        }
        metric_df = pd.DataFrame(
            [(k, v) for k, v in metrics.items() if pd.notna(v)],
            columns=["metric", "coverage"],
        )
        if not metric_df.empty:
            fig = px.bar(
                metric_df,
                x="metric",
                y="coverage",
                text="coverage",
                color="coverage",
                color_continuous_scale=["#c62828", "#f57c00", "#2e7d32"],
                labels={"metric": "", "coverage": "Coverage (%)"},
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_coloraxes(showscale=False)
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "**Full market**: vs. all IT jobs · "
            "**Role-aware**: vs. jobs matching this program's roles · "
            "**Core role-aware**: vs. core skills for those roles (primary metric) · "
            "**Weighted**: frequency-weighted core coverage"
        )

    st.markdown("---")

    # ── Shared computations (reused by tabs + PDF export) ───────────────────
    strengths = []
    if relevant_roles not in ("unmapped", "nan", ""):
        strengths = get_strengths(
            program, degree, relevant_roles, curriculum, course_skills, job_skills_by_role, n=20
        )

    doc_score = compute_program_doc_score(program, degree, curriculum, tiers)
    gap_type_global = "curriculum_gap" if doc_score >= 0.45 else ("documentation_gap" if doc_score <= 0.20 else "uncertain")

    prog_llm_gaps = llm_gaps[
        (llm_gaps["program_name"] == program) & (llm_gaps["degree_level"] == degree)
    ].sort_values("job_frequency", ascending=False)
    has_categories = not prog_llm_gaps.empty and "category" in prog_llm_gaps.columns

    if has_categories:
        gaps_list = [
            {"skill": r["missing_skill"], "job_frequency": r["job_frequency"]}
            for _, r in prog_llm_gaps.iterrows()
        ]
    else:
        prog_gaps = gaps[
            (gaps["program"] == program) & (gaps["degree"] == degree)
        ].sort_values("job_frequency", ascending=False)
        gaps_list = [
            {"skill": r["gap_skill"], "job_frequency": r["job_frequency"]}
            for _, r in prog_gaps.iterrows()
        ]

    # ── Export ────────────────────────────────────────────────────────────
    meta = load_run_metadata()
    pdf_bytes = build_program_pdf(
        university=current_university(),
        program=program,
        degree=degree,
        score=score,
        relevant_roles=relevant_roles,
        n_covered=n_covered,
        n_gap=n_gap,
        n_total=n_total,
        doc_score=doc_score,
        gap_type_label=GAP_TYPE_LABELS[gap_type_global],
        strengths=strengths,
        gaps=gaps_list,
        snapshot_date=meta["job_snapshot"]["collected_at"],
        benchmark=benchmark,
    )
    st.download_button(
        "📄 Export program brief (PDF)",
        data=pdf_bytes,
        file_name=f"{program.replace(' ', '_')}_{degree}_brief.pdf",
        mime="application/pdf",
    )

    st.markdown("---")

    # ── Tabs ────────────────────────────────────────────────────────────────
    tab_strengths, tab_gaps = st.tabs(["✅ Strengths", "⚠️ Gaps"])

    # ── Strengths tab ────────────────────────────────────────────────────────
    with tab_strengths:
        st.markdown(
            "Skills this program covers that are also in demand for its target roles. "
            "These form the program's market-relevant foundations."
        )

        if relevant_roles in ("unmapped", "nan", ""):
            st.info(
                "This program is not mapped to specific role groups, "
                "so a targeted strengths analysis is not available."
            )
        else:
            if not strengths:
                st.warning("No matching skills found between this program and its target roles.")
            else:
                for item in strengths:
                    count_str = f"  ·  {item['job_count']} job postings" if item["job_count"] else ""
                    st.markdown(f"✅ **{item['skill']}**{count_str}")

                st.caption(
                    f"Showing {len(strengths)} skills present in both this program and its target role job postings. "
                    f"Job count shows how many postings mention this skill."
                )

    # ── Gaps tab ────────────────────────────────────────────────────────────
    with tab_gaps:
        # Documentation quality notice
        if gap_type_global == "documentation_gap":
            st.warning(
                "⚠️ **Documentation quality notice**: Course descriptions for this program are limited. "
                "Some gaps listed below may be documentation gaps — the skills could already be taught "
                "but are not explicitly mentioned in course syllabi. "
                "Updating course descriptions may improve alignment scores without curriculum changes."
            )
        elif gap_type_global == "uncertain":
            st.info(
                "ℹ️ Course description coverage is mixed for this program. "
                "Some gaps may reflect incomplete documentation rather than true curriculum gaps."
            )

        if has_categories:
            categories = prog_llm_gaps["category"].dropna().unique()
            for cat in sorted(categories):
                cat_gaps = prog_llm_gaps[prog_llm_gaps["category"] == cat]
                icon = CATEGORY_ICONS.get(cat, "🔹")
                with st.expander(f"{icon} {cat} ({len(cat_gaps)} gaps)", expanded=True):
                    for _, grow in cat_gaps.head(10).iterrows():
                        freq_str = f"  ·  {int(grow['job_frequency'])} job postings"
                        gap_icon = GAP_TYPE_ICONS[gap_type_global]
                        gap_label = GAP_TYPE_LABELS[gap_type_global]
                        st.markdown(f"{gap_icon} **{grow['missing_skill']}**{freq_str}   `{gap_label}`")
        else:
            # Fallback: unified gap_analysis.csv (no categories)
            prog_gaps = gaps[
                (gaps["program"] == program) & (gaps["degree"] == degree)
            ].sort_values("job_frequency", ascending=False)

            if prog_gaps.empty:
                st.success("No significant gaps identified for this program.")
            else:
                for _, grow in prog_gaps.head(25).iterrows():
                    freq_str = f"  ·  {int(grow['job_frequency'])} job postings"
                    gap_icon = GAP_TYPE_ICONS[gap_type_global]
                    gap_label = GAP_TYPE_LABELS[gap_type_global]
                    st.markdown(f"{gap_icon} **{grow['gap_skill']}**{freq_str}   `{gap_label}`")

        # Gap type legend
        st.markdown("---")
        st.caption(
            "🔴 **Likely curriculum gap** — skill is absent and descriptions provide no related evidence  \n"
            "🟡 **Possible documentation gap** — skill may be taught but is not clearly described in syllabi  \n"
            "⚪ **Unclear** — insufficient evidence to classify"
        )
        st.caption(
            f"Documentation quality score for this program: **{doc_score:.0%}** "
            f"(proportion of extracted skills with high extraction confidence)"
        )



_render()
