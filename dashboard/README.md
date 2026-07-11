# Dashboard
Interactive dashboard for exploring the thesis data and results.

## Run

From the repository root:

```bash
python -m pip install -r dashboard/requirements.txt
python main.py
```

Then open [http://localhost:8501](http://localhost:8501).

You can also run Streamlit directly:

```bash
streamlit run dashboard/app.py
```

The dashboard reads the committed processed outputs. It does not rerun scraping, LLM extraction, or alignment computation.

## Sections

- Overview: headline dataset counts and dynamic summary charts
- Curriculum Explorer: filter courses by university, degree, program, and search text
- Job Postings Explorer: filter IT job postings by role, source, company, and search text
- Alignment Results: compare coverage by experiment, university, program, degree, and role group
- Skill Gaps: inspect missing high-demand skills by program
- Visual Summary: dashboard-native charts regenerated from processed data
- Reuse Guide: notes for adapting the same pipeline to another field
