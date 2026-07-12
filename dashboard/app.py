from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.auth_ui import can_switch_university, render_sidebar_identity, render_university_banner, require_login
from src.theme import inject_theme

st.set_page_config(
    page_title="CurriculumLens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

user = require_login()  # renders the login form and st.stop()s if not authenticated

pages = {
    "Methodology": [
        st.Page("pages/evidence.py", title="Methodology", icon="📐"),
    ],
    "Dashboard": [
        st.Page("pages/overview.py", title="Overview", icon="🏠"),
        st.Page("pages/programs.py", title="Programs", icon="📚"),
        st.Page("pages/program_detail.py", title="Program Detail", icon="🔍"),
        st.Page("pages/recommendations.py", title="Recommendations", icon="🧭"),
        st.Page("pages/job_fit.py", title="Job Fit", icon="💼"),
    ],
}
if can_switch_university():
    pages["Dashboard"].append(
        st.Page("pages/all_universities.py", title="All Universities", icon="🌍")
    )
pages["About"] = [st.Page("pages/admin.py", title="Data & Admin", icon="⚙️")]

pg = st.navigation(pages)

with st.sidebar:
    st.markdown("### 📊 CurriculumLens")
    render_sidebar_identity()
    st.markdown("---")

render_university_banner()
pg.run()
