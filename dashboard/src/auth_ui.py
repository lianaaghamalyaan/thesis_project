"""Login gate and university-visibility resolution for the Streamlit dashboard.

Visibility rule (system_architecture_plan.md §9):
- org_type == "university": locked to their own university, no switcher.
- org_type in ("policy", "internal"): full switcher across all universities,
  plus an "All Universities" comparison view.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from server.auth import authenticate
from server.queries import list_universities


def render_login() -> None:
    st.title("CurriculumLens")
    st.caption("Curriculum – labor market alignment for Armenian universities")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in", use_container_width=True)
    if submitted:
        user = authenticate(email, password)
        if user is None:
            st.error("Incorrect email or password.")
        else:
            st.session_state["user"] = user
            if user["org_type"] == "university":
                st.session_state["current_university"] = _university_name_for(user["university_id"])
            else:
                universities = list_universities()
                st.session_state["current_university"] = universities[0] if universities else None
            st.rerun()


def _university_name_for(university_id: int) -> str | None:
    from server.db import get_session
    from server.models import University

    session = get_session()
    try:
        uni = session.get(University, university_id)
        return uni.name if uni else None
    finally:
        session.close()


def require_login() -> dict:
    """Call at the top of app.py. Stops the script (renders login form) if
    not authenticated. Returns the session user dict otherwise."""
    if "user" not in st.session_state:
        render_login()
        st.stop()
    return st.session_state["user"]


def current_university() -> str | None:
    """The university whose data the current page should show. None means
    'all universities' (only reachable by policy/superadmin — see
    render_sidebar_identity's switcher, which never offers that option for
    university accounts)."""
    return st.session_state.get("current_university")


def can_switch_university() -> bool:
    user = st.session_state.get("user", {})
    return user.get("org_type") in ("policy", "internal")


def render_sidebar_identity() -> None:
    user = st.session_state.get("user")
    if not user:
        return
    st.sidebar.markdown(f"**{user['full_name']}**")
    st.sidebar.caption(f"{user['org_name']} · {user['role']}")

    if not can_switch_university():
        st.sidebar.caption(f"\U0001f4cc {current_university()}")

    if st.sidebar.button("Log out", use_container_width=True):
        for key in ("user", "current_university"):
            st.session_state.pop(key, None)
        st.rerun()


def render_university_banner() -> None:
    """Prominent, main-content-area university selector for policy/internal
    (admin) accounts — replaces a small sidebar dropdown that was easy to
    miss when switching between universities' data. Renders nothing for
    university-tier accounts (they have no switch to make)."""
    if not can_switch_university():
        return

    universities = list_universities()
    current = current_university()
    idx = universities.index(current) if current in universities else 0

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1F6F78 0%,#153F45 100%);
                    color:white;border-radius:12px;padding:10px 22px 4px 22px;margin-bottom:10px;">
            <div style="font-size:0.78em;text-transform:uppercase;letter-spacing:0.08em;opacity:0.85;">
                Admin view · currently viewing
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox(
            "University", universities, index=idx, key="university_switcher",
            label_visibility="collapsed",
        )
    with col2:
        user = st.session_state.get("user", {})
        st.caption(f"👁️ Viewing as {user.get('role') or user.get('org_type') or 'admin'}")
    if selected != current:
        st.session_state["current_university"] = selected
        st.rerun()
