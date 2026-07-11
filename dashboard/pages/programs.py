from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from src.data_loader import load_alignment, load_gaps
from src.formatting import format_score, score_color, score_label, roles_short


def _render():
    alignment = load_alignment()
    gaps = load_gaps()

    st.title("Programs")
    st.markdown("Select a program to see its full alignment breakdown.")

    # ── Filters ───────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        degrees = ["All"] + sorted(alignment["degree"].dropna().unique().tolist())
        selected_degree = st.selectbox("Degree level", degrees)
    with c2:
        query = st.text_input("Search by program name", placeholder="e.g. Data Science, Information Security…")

    filtered = alignment.copy()
    if selected_degree != "All":
        filtered = filtered[filtered["degree"] == selected_degree]
    if query:
        filtered = filtered[filtered["program"].str.contains(query, case=False, na=False)]

    filtered = filtered.sort_values("core_role_coverage_pct", ascending=False, na_position="last")

    st.caption(f"Showing {len(filtered)} program{'s' if len(filtered)!=1 else ''}")

    # ── Program cards ─────────────────────────────────────────────────────────
    for _, row in filtered.iterrows():
        program = row["program"]
        degree = row["degree"]
        score = row.get("core_role_coverage_pct")
        relevant_roles = str(row.get("relevant_roles", ""))
        n_gap = int(row.get("core_n_gap", 0)) if pd.notna(row.get("core_n_gap")) else None
        n_covered = int(row.get("core_n_overlap", 0)) if pd.notna(row.get("core_n_overlap")) else None

        color = score_color(score)
        label = score_label(score)

        with st.container(border=True):
            col_info, col_score, col_btn = st.columns([5, 2, 1])

            with col_info:
                st.markdown(f"**{program}**")
                st.caption(f"{degree} · {roles_short(relevant_roles)}")
                if n_covered is not None and n_gap is not None:
                    st.caption(f"Covers {n_covered} skills · {n_gap} gaps identified")

            with col_score:
                st.markdown(
                    f'<div style="text-align:center;padding:8px 0">'
                    f'<div style="font-size:1.6em;font-weight:700;color:{color}">'
                    f'{format_score(score)}</div>'
                    f'<div style="font-size:0.8em;color:{color}">{label}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col_btn:
                st.markdown("<div style='padding-top:12px'>", unsafe_allow_html=True)
                if st.button("View →", key=f"view_{program}_{degree}"):
                    st.session_state["selected_program"] = program
                    st.session_state["selected_degree"] = degree
                    st.switch_page("pages/program_detail.py")
                st.markdown("</div>", unsafe_allow_html=True)


_render()
