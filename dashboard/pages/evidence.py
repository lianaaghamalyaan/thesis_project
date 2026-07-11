from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.data_loader import load_run_metadata


def _render():
    meta = load_run_metadata()

    st.title("How it works")
    st.markdown("A brief explanation of how alignment scores are computed and what they mean.")

    st.subheader("What the score measures")
    with st.container(border=True):
        st.markdown(
            """
**Alignment score** = the percentage of skills commonly required in relevant IT job postings
that a program's courses explicitly cover.

| Score | Meaning |
|---|---|
| 50%+ | **Strong** — covers over half the role-relevant market skills |
| 35–50% | **Good** — solid coverage with targeted gaps |
| 25–35% | **Moderate** — clear opportunities to strengthen alignment |
| Below 25% | **Developing** — significant gaps or documentation issues likely |

A lower score does not mean the program is poor. No program is expected to cover every employer skill.
The score reflects what is *documented* in syllabi, not everything that may be taught in lectures.
            """
        )

    st.markdown("---")

    st.subheader("How it's computed")
    with st.container(border=True):
        st.markdown(
            """
1. Skills are extracted from course descriptions using an LLM (GPT-4o-mini).
2. The same extraction is applied to each IT job posting.
3. Both skill sets are normalized to the **ESCO taxonomy (v1.2)** so that equivalent terms match.
4. For each program, the score is: *skills required by relevant job roles that the program covers ÷ total skills required by those roles*.

The primary metric (**core role-aware coverage**) focuses on the roles most relevant to each program —
a Data Science program is compared against Data / ML / AI roles, not all IT jobs.
            """
        )

    st.markdown("---")

    st.subheader("Documentation gaps vs. curriculum gaps")
    with st.container(border=True):
        st.markdown(
            """
A skill in the **gaps list** may be missing for two different reasons:

- **Curriculum gap** — the skill is genuinely not taught. Requires adding content.
- **Documentation gap** — the skill is taught but the published syllabus doesn't mention it.
  Can be fixed by updating course descriptions, without changing what is taught.

Programs with vague or short course descriptions tend to show lower scores even when
the actual teaching content is strong. The Program Detail page flags this where relevant.
            """
        )

    st.markdown("---")
    st.caption(
        f"Data snapshot: {meta['run_id']} · {meta['job_snapshot']['n_it_postings']:,} IT job postings · "
        f"collected {meta['job_snapshot']['collected_at']} · ESCO {meta['esco_version']}"
    )


_render()
