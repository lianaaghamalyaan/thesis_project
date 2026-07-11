from datetime import date, datetime

import streamlit as st


def compute_freshness(meta: dict) -> dict:
    """Freshness status of the job market snapshot backing the current scores."""
    collected_at = meta["job_snapshot"]["collected_at"]
    collected_date = datetime.strptime(collected_at, "%Y-%m-%d").date()
    days_old = (date.today() - collected_date).days

    if days_old <= 30:
        status, color = "Fresh", "#2e7d32"
    elif days_old <= 90:
        status, color = "Aging", "#f57c00"
    else:
        status, color = "Stale — refresh recommended", "#c62828"

    return {
        "collected_at": collected_at,
        "days_old": days_old,
        "status": status,
        "color": color,
        "n_postings": meta["job_snapshot"]["n_it_postings"],
        "is_static": meta.get("job_snapshot", {}).get("window") == "static",
    }


def render_freshness_banner(meta: dict) -> None:
    """Compact banner showing when job data was last refreshed."""
    f = compute_freshness(meta)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:8px 14px;'
        f'background:#f8f9fa;border-radius:8px;border-left:4px solid {f["color"]};'
        f'margin-bottom:10px;font-size:0.85em;color:#444">'
        f'<span style="font-weight:700;color:{f["color"]}">● {f["status"]}</span>'
        f'<span>Job data as of <b>{f["collected_at"]}</b> ({f["days_old"]} days ago)</span>'
        f'<span>·</span>'
        f'<span><b>{f["n_postings"]:,}</b> IT postings in snapshot</span>'
        f"</div>",
        unsafe_allow_html=True,
    )
    if f["is_static"]:
        st.caption(
            "⚠️ This is a static research snapshot, not a live feed. "
            "Scores will not change until the job data is refreshed."
        )
