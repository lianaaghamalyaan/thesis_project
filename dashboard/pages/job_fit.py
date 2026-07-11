from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.data_loader import (
    load_alignment,
    load_course_skills,
    load_curriculum,
    load_job_skills_by_role,
)
from src.job_fit_engine import compute_job_fit
from src.formatting import format_score, score_color


ROLE_DESCRIPTIONS = {
    "Backend": "Server-side development, APIs, databases, and system architecture",
    "Data / ML / AI": "Data analysis, machine learning, model development, and data pipelines",
    "DevOps / Cloud": "Infrastructure, cloud platforms, CI/CD, containers, and automation",
    "Frontend / JS": "Web UI development, JavaScript frameworks, and browser technologies",
    "Full Stack": "End-to-end web development across frontend and backend",
    "Hardware / Embedded": "Embedded systems, firmware, hardware design, and low-level programming",
    "Mobile": "iOS and Android app development",
    "QA / Testing": "Software testing, test automation, and quality assurance",
    "Security": "Cybersecurity, penetration testing, secure coding, and compliance",
}


def _render():
    alignment = load_alignment()
    curriculum = load_curriculum()
    course_skills = load_course_skills()
    job_skills_by_role = load_job_skills_by_role()

    st.title("Job Fit Comparison")
    st.markdown(
        "Compare a program's skill coverage against a specific job role. "
        "See what is already covered and what is missing."
    )

    # ── Selectors ─────────────────────────────────────────────────────────
    col_prog, col_role = st.columns(2)

    with col_prog:
        program_options = [
            (row["program"], row["degree"])
            for _, row in alignment.sort_values("core_role_coverage_pct", ascending=False, na_position="last").iterrows()
        ]
        program_labels = [f"{p} ({d})" for p, d in program_options]

        default_idx = 0
        saved_program = st.session_state.get("selected_program")
        saved_degree = st.session_state.get("selected_degree")
        if saved_program and saved_degree:
            for i, (p, d) in enumerate(program_options):
                if p == saved_program and d == saved_degree:
                    default_idx = i
                    break

        selected_prog_label = st.selectbox("Program", program_labels, index=default_idx)
        prog_idx = program_labels.index(selected_prog_label)
        program, degree = program_options[prog_idx]

    with col_role:
        available_roles = sorted(job_skills_by_role.keys())
        selected_role = st.selectbox(
            "Target job role",
            available_roles,
            help="Select the role you want to compare this program against.",
        )

    st.markdown(
        f'<p style="color:#555;font-size:0.9em">📌 {ROLE_DESCRIPTIONS.get(selected_role, "")}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Compute ────────────────────────────────────────────────────────────
    with st.spinner("Computing fit…"):
        result = compute_job_fit(program, degree, selected_role, curriculum, course_skills, job_skills_by_role)

    if result["match_score"] is None:
        st.error(f"No skill data available for the **{selected_role}** role group.")
        return

    match_score = result["match_score"]
    matched = result["matched"]
    missing = result["missing"]
    n_role = result["n_role_skills"]
    n_prog = result["n_program_skills"]

    # ── Match overview ──────────────────────────────────────────────────────
    color = score_color(match_score)

    st.markdown(
        f'<div style="text-align:center;padding:20px 0">'
        f'<div style="font-size:0.9em;color:#555">Match score for <strong>{program} ({degree})</strong> vs <strong>{selected_role}</strong></div>'
        f'<div style="font-size:3em;font-weight:800;color:{color}">{match_score:.1f}%</div>'
        f'<div style="font-size:0.9em;color:#555">'
        f'{len(matched)} of {n_role} role skills covered · {n_prog} skills in program</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Match score progress bar
    st.progress(min(match_score / 100, 1.0))

    # Context
    with st.container(border=True):
        if match_score >= 50:
            st.markdown(
                f"✅ **Good fit**: This program covers a majority of skills commonly required for **{selected_role}** roles."
            )
        elif match_score >= 25:
            st.markdown(
                f"🟡 **Partial fit**: This program covers foundational skills for **{selected_role}** roles, "
                f"but there are significant gaps in applied tooling and specialised knowledge."
            )
        else:
            st.markdown(
                f"🔴 **Limited fit**: This program currently covers a small proportion of skills required for **{selected_role}** roles. "
                f"There may be opportunities to add electives or adjust course content for students targeting this path."
            )

    st.markdown("---")

    # ── Matched and missing ────────────────────────────────────────────────
    col_match, col_miss = st.columns(2)

    with col_match:
        st.subheader(f"✅ Covered ({len(matched)} skills)")
        st.caption("Skills required by this role that the program already covers")
        if not matched:
            st.info("No matched skills found.")
        else:
            for item in matched[:20]:
                count_str = f"  ·  {item['job_count']} jobs" if item["job_count"] else ""
                st.markdown(f"✅ **{item['skill']}**{count_str}")
            if len(matched) > 20:
                st.caption(f"+ {len(matched) - 20} more covered skills")

    with col_miss:
        st.subheader(f"⚠️ Missing ({len(missing)} skills)")
        st.caption("Skills this role commonly requires that are not in the program")
        if not missing:
            st.success("No significant missing skills found.")
        else:
            for item in missing[:20]:
                count_str = f"  ·  {item['job_count']} jobs"
                st.markdown(f"⚠️ **{item['skill']}**{count_str}")
            if len(missing) > 20:
                with st.expander(f"Show all {len(missing)} missing skills"):
                    for item in missing[20:]:
                        st.markdown(f"— {item['skill']}")

    st.markdown("---")

    # ── Action framing ─────────────────────────────────────────────────────
    st.subheader("What this means")
    top_missing = [item["skill"] for item in missing[:3]]
    if top_missing:
        st.markdown(
            f"For students from this program aiming for **{selected_role}** roles, "
            f"the most important skills to develop outside the curriculum are: "
            f"**{', '.join(top_missing)}**."
        )
    st.markdown(
        "For the curriculum committee, this comparison highlights where electives, "
        "practical labs, or updated course content could improve graduate readiness for this specific role path."
    )
    st.caption(
        "Note: This comparison uses skills extracted from course descriptions and skills aggregated from "
        "Armenian IT job postings. Results depend on description quality."
    )

    # ── Navigate back ────────────────────────────────────────────────────────
    if st.button("← Back to Program Detail"):
        st.switch_page("pages/program_detail.py")


_render()
