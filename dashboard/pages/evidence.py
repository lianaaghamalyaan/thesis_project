from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.data_loader import load_run_metadata


def _render():
    meta = load_run_metadata()

    st.title("📐 Methodology")
    st.markdown(
        "How alignment scores are computed, what the numbers mean, and where the "
        "underlying data comes from — the full technical picture in one place, "
        "without needing to read the source code."
    )

    st.markdown("---")

    st.subheader("What the score measures")
    with st.container(border=True):
        st.markdown(
            """
**Core role-aware coverage** (the headline number shown throughout the dashboard) =
the percentage of skills commonly required in job postings for roles relevant to a program
that the program's courses demonstrably cover.

| Score | Meaning |
|---|---|
| 50%+ | **Strong** — covers over half the role-relevant market skills |
| 35–50% | **Good** — solid coverage with targeted gaps |
| 25–35% | **Moderate** — clear opportunities to strengthen alignment |
| Below 25% | **Developing** — significant gaps or documentation issues likely |

A lower score does not mean a program is poor. No program is expected to cover every skill an
employer might list — job postings routinely wishlist skills far beyond what any single degree
could reasonably teach. The score reflects what is *documented* in course descriptions, not
necessarily everything an instructor actually covers in a lecture.
            """
        )

    st.markdown("---")

    st.subheader("Pipeline, step by step")
    with st.container(border=True):
        st.markdown(
            """
1. **Skill extraction.** An LLM extracts a normalized list of skill phrases from each course
   description and each job posting's full text independently.
2. **Skill consolidation.** Raw skill phrases are highly redundant — "AWS" and "Amazon Web
   Services" describe one real skill. All extracted phrases (course-side and job-side together)
   are embedded with a sentence-transformer model and greedily clustered at **cosine similarity
   ≥ 0.85**; the most frequent phrase in each cluster becomes that cluster's canonical name.
   This plays the deduplication role a fixed external taxonomy (e.g. ESCO) would otherwise play,
   without being limited to that taxonomy's vocabulary — useful since current tech terms
   (Docker, Kubernetes, RAG, etc.) are often missing or outdated in general-purpose skill
   taxonomies.
3. **Matching.** A program's consolidated skills are compared against a job market's consolidated
   skills via **bidirectional cosine similarity ≥ 0.65**: a market skill counts as covered if some
   program skill is semantically close enough to it (and vice versa, for surplus detection). A
   small hand-curated **blocklist** prevents near-miss false positives between skills that are
   semantically close but functionally distinct (e.g. React vs. Angular, TypeScript vs.
   JavaScript, Docker vs. Kubernetes) and an **allowlist** captures a few well-established
   implications below that threshold (e.g. Python implying basic NumPy/Pandas exposure,
   PostgreSQL implying SQL).
4. **Role scoping.** Each program is mapped to the job-market role group(s) most relevant to it
   (e.g. a Data Science program is scored against Data / ML / AI postings, not the full IT
   market). Programs mapped to more than one role have their **core skill sets unioned across
   all relevant roles**, and one coverage number is computed against that union.
5. **"Core" skill filtering.** Within a program's relevant role(s), a market skill counts as
   **core** if it appears in at least **5% of that role's own postings** — this excludes rare,
   idiosyncratic skill mentions from the denominator so the score reflects genuinely common
   market demand, not noise.
6. **Weighting.** The secondary **weighted core coverage** metric — the figure emphasized
   throughout the underlying thesis research — weights each core skill's contribution by its
   posting frequency rather than counting all core skills equally. This avoids penalizing
   specialist programs for not covering every low-frequency core skill as heavily as missing a
   skill that appears in most postings for that role.
            """
        )

    st.markdown("---")

    st.subheader("Documentation gaps vs. curriculum gaps")
    with st.container(border=True):
        st.markdown(
            """
A skill in the **gaps list** may be missing for two different reasons:

- 🔴 **Curriculum gap** — the skill is genuinely not taught. Requires adding content.
- 🟡 **Documentation gap** — the skill is likely taught but the published course description
  doesn't mention it explicitly (flagged using confidence tiers from the skill-extraction step).
  Can potentially be fixed by improving course descriptions, without changing what is taught.
- ⚪ **Uncertain** — not enough signal either way.

Programs with vague or short course descriptions tend to show lower scores even when the actual
teaching content is strong. The Program Detail page flags this distinction where relevant.
            """
        )

    st.markdown("---")

    st.subheader("Reproducibility & data snapshot")
    with st.container(border=True):
        job_snap = meta.get("job_snapshot", {})
        curr_snap = meta.get("curriculum_snapshot", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Job postings in scope", f"{job_snap.get('n_it_postings', '—'):,}" if isinstance(job_snap.get("n_it_postings"), int) else "—")
            st.caption(f"Collected: {job_snap.get('collected_at', '—')}")
        with c2:
            st.metric("Programs", curr_snap.get("n_programs", "—"))
            st.caption(f"Courses: {curr_snap.get('n_courses', '—'):,}" if isinstance(curr_snap.get("n_courses"), int) else "")
        with c3:
            st.metric("Universities", curr_snap.get("n_universities", "—"))
            st.caption(f"Run: `{meta.get('run_id', '—')}`")

        st.markdown(
            """
Every alignment score shown in this dashboard is traceable to a specific **run** — a single
execution of the pipeline above against a specific snapshot of curriculum and job-market data.
Historical runs are preserved, not overwritten, when the pipeline is re-run with fresh data.
            """
        )
        if meta.get("notes"):
            st.caption(f"Run notes: {meta['notes']}")

    st.markdown("---")
    st.caption(
        f"Data snapshot: {meta.get('run_id', '—')} · "
        f"{job_snap.get('n_it_postings', '—')} IT job postings · "
        f"collected {job_snap.get('collected_at', '—')}"
    )


_render()
