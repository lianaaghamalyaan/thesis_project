from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from server import queries

MIN_ROLE_MATCHED_PEERS = 3


@st.cache_data(show_spinner=False)
def load_all_universities_alignment() -> pd.DataFrame:
    """Alignment results for every university (canonical experiment only).

    Deliberately unfiltered by session/current_university — this is the
    backend-sees-everything half of the visibility model (system_architecture
    _plan.md §9): a university's own benchmarks and suggestions are computed
    from every other university's data, even though the UI only ever shows
    the requesting university anonymized peer statistics, never named ones.
    """
    return queries.load_alignment(university=None)


def _roles_overlap(roles_str, target_roles: set) -> bool:
    if not isinstance(roles_str, str) or roles_str in ("unmapped", "nan", ""):
        return False
    roles = {r.strip() for r in roles_str.split(",")}
    return bool(roles & target_roles)


def peer_benchmark(university: str, degree: str, relevant_roles: str):
    """
    Compare a program's score against peer programs at other universities.
    Prefers peers with an overlapping role group; falls back to same-degree
    peers across all universities if too few role-matched peers exist.

    Returns None if there is no usable peer data at all.
    """
    all_alignment = load_all_universities_alignment()

    others = all_alignment[
        (all_alignment["university"] != university)
        & (all_alignment["degree"] == degree)
        & (all_alignment["core_role_coverage_pct"].notna())
    ].copy()

    if others.empty:
        return None

    matched_on = "degree level"
    if relevant_roles and relevant_roles not in ("unmapped", "nan", "", "ALL"):
        target_roles = {r.strip() for r in str(relevant_roles).split(",")}
        role_matched = others[others["relevant_roles"].apply(_roles_overlap, target_roles=target_roles)]
        if len(role_matched) >= MIN_ROLE_MATCHED_PEERS:
            others = role_matched
            matched_on = "role group"

    return {
        "peer_mean": float(others["core_role_coverage_pct"].mean()),
        "peer_median": float(others["core_role_coverage_pct"].median()),
        "peer_max": float(others["core_role_coverage_pct"].max()),
        "peer_n": int(len(others)),
        "matched_on": matched_on,
    }


def render_benchmark_panel(score, university: str, degree: str, relevant_roles: str) -> dict | None:
    """Renders the peer comparison panel and returns the benchmark dict (or None)."""
    bm = peer_benchmark(university, degree, relevant_roles)
    if bm is None or score is None or pd.isna(score):
        return bm

    delta = score - bm["peer_mean"]
    delta_color = "#2e7d32" if delta >= 0 else "#c62828"
    delta_sign = "+" if delta >= 0 else ""

    st.markdown("##### 📊 How this compares")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("This program", f"{score:.1f}%")
    with c2:
        st.metric(f"Peer average (n={bm['peer_n']})", f"{bm['peer_mean']:.1f}%")
    with c3:
        st.metric("Difference", f"{delta_sign}{delta:.1f} pts", delta=f"{delta_sign}{delta:.1f}")

    st.caption(
        f"Compared against {bm['peer_n']} programs at other Armenian universities, "
        f"matched by {bm['matched_on']}. Peer best observed: {bm['peer_max']:.1f}%."
    )
    return bm
