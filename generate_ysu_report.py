"""
generate_ysu_report.py — YSU IT Curriculum Alignment: Decision-Support Report
Run: python generate_ysu_report.py
Output: ysu_alignment_report.pdf
"""
from __future__ import annotations
import json, os, shutil, tempfile
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether,
    NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ─── PATHS ───────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent
PROC   = ROOT / "data" / "processed"
OUT    = ROOT / "ysu_alignment_report.pdf"
TMPDIR = tempfile.mkdtemp(prefix="ysu_report_")

# ─── COLOUR PALETTE (modern, clean) ─────────────────────────────────────────
DARK       = "#0F172A"
BLUE       = "#1D4ED8"
BLUE_BG    = "#EFF6FF"
BODY_C     = "#1E293B"
MUTED      = "#64748B"
BORDER     = "#E2E8F0"
BG         = "#F8FAFC"
GREEN      = "#3D7A5F"
GREEN_BG   = "#EDF8F2"
GREEN_LT   = "#C8E8D8"
TEAL       = "#2E7A94"
TEAL_BG    = "#E5F3F8"
ORANGE     = "#A07830"
ORANGE_BG  = "#FAF4E6"
RED        = "#A05252"
RED_BG     = "#FAF0F0"

W, H = A4   # 595.2 × 841.9 pt
MARGIN = 2.2 * cm
CONTENT_W = W - 2 * MARGIN

def c(h): return colors.HexColor(h)

def score_hex(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return MUTED
    if v >= 50: return GREEN
    if v >= 35: return TEAL
    if v >= 25: return ORANGE
    return RED

def score_bg(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return BG
    if v >= 50: return GREEN_BG
    if v >= 35: return TEAL_BG
    if v >= 25: return ORANGE_BG
    return RED_BG

def score_label(v):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "No data"
    if v >= 50: return "Strong"
    if v >= 35: return "Good"
    if v >= 25: return "Moderate"
    return "Developing"

# ─── DATA ────────────────────────────────────────────────────────────────────
print("Loading data…")
curriculum_all = pd.read_csv(PROC / "curriculum/final_curriculum_dataset.csv")
curriculum = curriculum_all[curriculum_all["university"] == "Yerevan State University"].reset_index(drop=True)

alignment_all = pd.read_csv(PROC / "unified/alignment_results.csv")
alignment = alignment_all[
    (alignment_all["experiment"] == "LLM_desc_semantic") &
    (alignment_all["university"] == "Yerevan State University")
].reset_index(drop=True)

gaps_all = pd.read_csv(PROC / "unified/gap_analysis.csv")
gaps = gaps_all[gaps_all["university"] == "Yerevan State University"].reset_index(drop=True)

llm_gaps_all = pd.read_csv(PROC / "llm_skills/llm_gap_analysis.csv")
llm_gaps = llm_gaps_all[llm_gaps_all["university"] == "Yerevan State University"].reset_index(drop=True)

with open(PROC / "unified/course_skills_names_only.json") as f:
    course_skills = json.load(f)
with open(PROC / "unified/course_confidence_tiers.json") as f:
    tiers_data = json.load(f)
with open(ROOT / "data/runs/march_2026_static/metadata.json") as f:
    meta = json.load(f)

it_jobs = pd.read_csv(PROC / "jobs/final_jobs_dataset_it_only.csv")
with open(PROC / "unified/job_skills_by_id.json") as f:
    js_raw = json.load(f)

# Joined by stable job_id (sha1 of source_url), not row position — see
# pipeline/migrations/001_stable_job_id.py. Coverage is partial: postings
# added after the last LLM extraction run have no entry here.
job_skills_by_role: dict[str, Counter] = {}
for _, row in it_jobs.iterrows():
    skills = js_raw.get(row["job_id"])
    if not skills:
        continue
    role = row["it_role_group"]
    if isinstance(role, str):
        job_skills_by_role.setdefault(role, Counter())
        for s in skills:
            job_skills_by_role[role][s] += 1

# ─── PROGRAM CONFIG ──────────────────────────────────────────────────────────
PROGRAM_ORDER = [
    ("Data Science in Business", "Master"),
    ("Applied Statistics and Data Science", "Master"),
    ("Applied Statistics and Data Science", "Bachelor"),
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"),
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"),
    ("Information Systems Management", "Master"),
    ("Information Systems Development", "Master"),
    ("Information Security", "Bachelor"),
    ("Discrete Mathematics and Theoretical Informatics", "Master"),
    ("Numerical Analysis and Mathematical Modelling", "Master"),
    ("Radiophysics and Computer Technology", "Bachelor"),
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"),
    ("Informatics and Applied Mathematics", "Bachelor"),
]

SHORT_NAMES = {
    "Data Science in Business": "Data Science in Business",
    "Applied Statistics and Data Science": "Applied Statistics & Data Science",
    "Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks": "Math & SW Dev of Computing Systems",
    "Data Processing in Physics and Artificial Intelligence": "Data Processing in Physics & AI",
    "Information Systems Management": "Information Systems Management",
    "Information Systems Development": "Information Systems Development",
    "Information Security": "Information Security",
    "Discrete Mathematics and Theoretical Informatics": "Discrete Math & Theoretical Informatics",
    "Numerical Analysis and Mathematical Modelling": "Numerical Analysis & Math Modelling",
    "Radiophysics and Computer Technology": "Radiophysics & Computer Technology",
    "Informatics and Applied Mathematics (Part time)": "Informatics & Applied Math (Part-time)",
    "Informatics and Applied Mathematics": "Informatics & Applied Mathematics",
}

FACULTY_MAP = {
    ("Data Science in Business", "Master"): "Faculty of Economics & Management",
    ("Applied Statistics and Data Science", "Master"): "Faculty of Mathematics & Mechanics",
    ("Applied Statistics and Data Science", "Bachelor"): "Faculty of Mathematics & Mechanics",
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"): "Faculty of Physics",
    ("Information Systems Management", "Master"): "IT Educational & Research Center",
    ("Information Systems Development", "Master"): "IT Educational & Research Center",
    ("Information Security", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
    ("Discrete Mathematics and Theoretical Informatics", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Numerical Analysis and Mathematical Modelling", "Master"): "Faculty of Informatics & Applied Mathematics",
    ("Radiophysics and Computer Technology", "Bachelor"): "Faculty of Radiophysics",
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
    ("Informatics and Applied Mathematics", "Bachelor"): "Faculty of Informatics & Applied Mathematics",
}

PROGRAM_URLS = {
    ("Applied Statistics and Data Science", "Bachelor"): "https://ysu.am/en/faculty/516/educational-program-299/edu-plan",
    ("Applied Statistics and Data Science", "Master"):   "https://ysu.am/en/faculty/516/educational-program-303/edu-plan",
    ("Blockchain and Digital Currencies",   "Master"):   "https://ysu.am/en/faculty/516/educational-program-957/edu-plan",
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"): "https://ysu.am/en/faculty/525/educational-program-313/edu-plan",
    ("Data Science in Business",            "Master"):   "https://ysu.am/en/faculty/78/educational-program-349/edu-plan",
    ("Discrete Mathematics and Theoretical Informatics", "Master"): "https://ysu.am/en/faculty/85/educational-program-306/edu-plan",
    ("Informatics and Applied Mathematics", "Bachelor"): "https://ysu.am/en/faculty/85/educational-program-305/edu-plan",
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"): "https://ysu.am/en/faculty/85/educational-program-309/edu-plan",
    ("Information Security",                "Bachelor"): "https://ysu.am/en/faculty/85/educational-program-304/edu-plan",
    ("Information Systems Development",     "Master"):   "https://ysu.am/en/faculty/520/educational-program-689/edu-plan",
    ("Information Systems Management",      "Master"):   "https://ysu.am/en/faculty/520/educational-program-500/edu-plan",
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"): "https://ysu.am/en/faculty/85/educational-program-308/edu-plan",
    ("Numerical Analysis and Mathematical Modelling", "Master"): "https://ysu.am/en/faculty/85/educational-program-307/edu-plan",
    ("Radiophysics and Computer Technology","Bachelor"): "https://ysu.am/en/faculty/525/educational-program-858/edu-plan",
}

ROLE_MAPPING = {
    "Software Engineering": ["Backend", "Full Stack", "General IT"],
    "Data / ML / AI": ["Data / ML / AI"],
    "DevOps / Cloud": ["DevOps / Cloud"],
    "Hardware / Embedded": ["Hardware / Embedded"],
    "Security": ["Security"],
    "QA / Testing": ["QA / Testing"],
    "IT Support / Admin / ERP": ["IT Support / Admin", "General IT"],
    "Technical Management": ["Technical Management"],
    "UX / Product Design": ["UX / Product Design"],
}


def build_program_narrative(prog, deg, score, doc_score, rel, n_gap, n_overlap):
    """Returns (interpretation, gap_type_label, actions_list).

    Numbers (score, doc_score, n_gap, n_overlap) are dynamic; qualitative prose is hand-authored.
    Uses 'may' not 'will' — description review is the way to FIND OUT which gaps are real.
    """
    sl   = score_label(score)
    ss   = f"{score:.1f}%"
    dqs  = f"{doc_score:.0%}"
    dq   = "limited" if doc_score < 0.25 else "mixed"

    narratives = {
        ("Data Science in Business", "Master"): (
            f"YSU's best-scoring program — {ss} — and 2nd in the country out of 40 mapped "
            "programs. Some of the listed gaps may already be taught in class but not written "
            "in published course descriptions. Check with faculty before making any changes.",
            "Check with faculty first — some gaps may be documentation issues",
            [
                "Ask faculty to go through the gap list and confirm which tools "
                "(e.g. Docker, CI/CD pipelines) are already taught but not listed in descriptions",
                "Update course descriptions to reflect what is actually delivered — "
                "this alone can close many measured gaps without any curriculum change",
                "For tools confirmed as genuinely absent, a short applied module on "
                "containerization and cloud deployment would be the most targeted addition",
            ]
        ),
        ("Applied Statistics and Data Science", "Master"): (
            f"Strong data science program with a score of {ss}. Most course descriptions are "
            "very brief, so many of the listed gaps may already be covered in lectures but "
            "not written down. The priority is to ask faculty to update course descriptions "
            "before assuming any curriculum changes are needed.",
            "Mostly documentation — descriptions are too brief to trust the gap list as-is",
            [
                "Ask faculty to add specific tools and methods to each course description "
                "(Python packages, statistical frameworks, ML tools used in class)",
                "After descriptions are updated, rerun this analysis — the score may "
                "change significantly and show fewer real gaps",
                "If cloud platforms or MLOps tools are confirmed genuinely absent, "
                "a short elective would be the right next step",
            ]
        ),
        ("Applied Statistics and Data Science", "Bachelor"): (
            f"Good undergraduate data program, scoring {ss}. Course descriptions are brief, "
            "so the gap list likely overstates what is truly missing. Update descriptions "
            "first — the score probably understates real coverage.",
            "Mostly documentation — update descriptions before deciding on any changes",
            [
                "Add specific tools and methods to course descriptions for data, "
                "statistics, and programming courses",
                "Rerun the analysis after updates — results may look quite different",
                "No curriculum changes recommended until descriptions are verified",
            ]
        ),
        ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"): (
            f"Solid software and systems program, scoring {ss}. Cloud deployment tools and "
            "containerization are likely genuine gaps. Review course descriptions with "
            "faculty first to confirm what is already taught.",
            "Mixed — some gaps are real (cloud tools); some may be documentation issues",
            [
                "Update course descriptions to name the specific tools and frameworks used",
                "Cloud deployment, Kubernetes, and CI/CD pipelines are likely genuine "
                "gaps — targeted additions would help graduates in these areas",
                "Rerun the analysis after description updates to confirm which gaps are real",
            ]
        ),
        ("Data Processing in Physics and Artificial Intelligence", "Bachelor"): (
            f"Good AI and computing content delivered within a physics program, scoring {ss}. "
            "Some gaps may not reflect what is actually taught — especially for AI methods. "
            "Update course descriptions to get a clearer picture.",
            "Mixed — AI content may be better covered than the score shows; check first",
            [
                "Update AI and machine learning course descriptions to name the "
                "algorithms, tools, and frameworks used in class",
                "Rerun the analysis after updates — the score may better reflect "
                "what is actually taught",
                "No curriculum changes recommended until descriptions are verified",
            ]
        ),
        ("Information Systems Management", "Master"): (
            f"Covers IT management and enterprise systems, scoring {ss}. Course descriptions "
            "are brief, so many listed gaps are likely documentation issues rather than "
            "missing content. Ask faculty to review before making any decisions.",
            "Mostly documentation — brief descriptions make the gap list unreliable",
            [
                "Ask faculty which tools and platforms are already taught but "
                "missing from published descriptions",
                "Update course descriptions with specific tool and platform names",
                "If cloud administration and scripting tools are confirmed genuinely "
                "absent, consider adding them — they are in growing demand",
            ]
        ),
        ("Information Systems Development", "Master"): (
            f"Solid IT development program, scoring {ss}. Modern web frameworks and cloud "
            "deployment are the most likely genuine gaps. Update descriptions first "
            "to confirm what is truly missing.",
            "Mixed — some real tooling gaps likely; verify with faculty first",
            [
                "Update course descriptions with specific frameworks, languages, "
                "and tools used in each course",
                "Modern web frameworks and cloud deployment are likely genuine gaps — "
                "consider targeted additions after verifying with faculty",
                "Rerun the analysis after updates to separate documentation from real gaps",
            ]
        ),
        ("Information Security", "Bachelor"): (
            f"Security is a broad field with many required skills, so a lower score like "
            f"{ss} is expected. The large gap count partly reflects the breadth of the "
            "field, not just missing content. Focus on the top 10–15 most common gaps "
            "rather than trying to address the full list.",
            "Mixed — broad field inflates gap count; verify before acting on individual items",
            [
                "Update descriptions for security courses to name specific tools "
                "and protocols already covered",
                "Cloud security and containerized environments are likely genuine gaps "
                "with high demand — worth prioritizing",
                f"Focus on the top 10–15 most common gaps first; "
                f"the full {n_gap}-item list is too broad to address at once",
            ]
        ),
        ("Discrete Mathematics and Theoretical Informatics", "Master"): (
            f"A theory-focused program — a lower score of {ss} is expected and appropriate, "
            "not a sign of a weak program. Job ads don't capture the value of formal "
            "reasoning and mathematical foundations that this program provides.",
            "Low score is expected by design — intentional theoretical focus",
            [
                "No curriculum changes recommended — this program serves a "
                "different purpose than industry-facing programs",
                "For any practical computing courses, update descriptions to "
                "document the tools used",
                "Consider a short guide for students explaining what career paths "
                "this theoretical background enables",
            ]
        ),
        ("Numerical Analysis and Mathematical Modelling", "Master"): (
            f"A deep mathematical program — the score of {ss} reflects what job ads can "
            "measure, not what this program is actually worth. No curriculum changes "
            "are recommended based on this score alone.",
            "Low score reflects measurement limits — not a program weakness",
            [
                "Update descriptions to name the programming languages and tools "
                "used in coursework (Python, MATLAB, R, numerical libraries)",
                "Rerun the analysis after updates — the score may better reflect "
                "the applied content",
                "No curriculum changes recommended based on this measurement",
            ]
        ),
        ("Radiophysics and Computer Technology", "Bachelor"): (
            f"A specialized program for hardware and physics roles — a smaller niche with "
            f"fewer job listings. The score of {ss} reflects the size of this niche. "
            "Updating course descriptions to name the tools used would help.",
            "Partly structural — small specialized field; descriptions also need updating",
            [
                "Update descriptions to name programming languages and hardware tools "
                "used in coursework (C/C++, FPGA tools, embedded platforms)",
                "Rerun the analysis after updates to get a clearer picture",
                "Modern embedded tools would strengthen alignment in a growing area",
            ]
        ),
        ("Informatics and Applied Mathematics (Part time)", "Bachelor"): (
            f"A broad foundations program compared against all IT fields at once. "
            f"The score of {ss} is a measurement effect — no broad program can cover "
            "every IT specialization. This number should not be used as-is for decisions.",
            "Score is a measurement effect — do not use as-is for decisions",
            [
                "Request a comparison against the 2–3 job roles most relevant to "
                "graduates — this would give a much more meaningful score",
                "Update descriptions for programming and mathematics courses with "
                "specific tools and language names",
                "Review this track together with the full-time track — they share "
                "most content",
            ]
        ),
        ("Informatics and Applied Mathematics", "Bachelor"): (
            f"Same situation as the part-time track: a broad program compared against all "
            f"IT fields at once. The score of {ss} reflects measurement breadth, not poor "
            "preparation. Request a targeted comparison for a meaningful result.",
            "Score is a measurement effect — same situation as the part-time track",
            [
                "Request a comparison against the 2–3 job roles most relevant to "
                "graduates for a more useful score",
                "Review this track together with the part-time track — they share "
                "most content",
                "Update descriptions for programming and mathematics courses with "
                "specific tool and language names",
            ]
        ),
    }

    default = (
        f"This program scored {ss} ({sl.lower()}) against its target roles. "
        f"Some of the {n_gap} listed gaps may already be taught but not written in "
        "published descriptions. Check with faculty before acting on the gap list.",
        "Check with faculty — some gaps may be documentation issues",
        [
            "Ask faculty to confirm which skills are already taught but "
            "not listed in published descriptions",
            "Update course descriptions to reflect actual teaching content",
        ]
    )

    return narratives.get((prog, deg), default)


# ─── COMPUTATION ─────────────────────────────────────────────────────────────
def expand_roles(rel):
    if not rel or str(rel) in ("unmapped", "nan", ""): return []
    result = []
    for r in str(rel).split(","):
        result.extend(ROLE_MAPPING.get(r.strip(), [r.strip()]))
    return list(dict.fromkeys(result))

def get_program_skills(prog, deg):
    crs = curriculum[(curriculum["program_name"] == prog) & (curriculum["degree_level"] == deg)]
    skills = set()
    for _, row in crs.iterrows():
        cid = str(int(row["course_id"]))
        skills.update(course_skills.get(cid, []))
    return skills

def get_role_counter(rel):
    agg = Counter()
    for role in expand_roles(rel):
        agg.update(job_skills_by_role.get(role, {}))
    return agg

def get_doc_score(prog, deg):
    crs = curriculum[(curriculum["program_name"] == prog) & (curriculum["degree_level"] == deg)]
    t1, total = 0, 0
    for _, row in crs.iterrows():
        cid = str(int(row["course_id"]))
        td = tiers_data.get(cid, {})
        t1 += len(td.get("tier1", []))
        total += len(td.get("combined", []))
    return t1 / total if total else 0.0

def get_matched(prog, deg, rel, n=12):
    ps = get_program_skills(prog, deg)
    rc = get_role_counter(rel)
    matched = [(s, rc[s]) for s in ps if s in rc]
    matched.sort(key=lambda x: -x[1])
    return matched[:n]

def get_missing(prog, deg, n=12):
    lg = llm_gaps[(llm_gaps["program_name"] == prog) & (llm_gaps["degree_level"] == deg)]
    if not lg.empty:
        return lg.sort_values("job_frequency", ascending=False).head(n)[
            ["missing_skill", "job_frequency", "category"]].to_dict("records")
    g2 = gaps[(gaps["program"] == prog) & (gaps["degree"] == deg)]
    return [{"missing_skill": r["gap_skill"], "job_frequency": r["job_frequency"], "category": ""}
            for _, r in g2.sort_values("job_frequency", ascending=False).head(n).iterrows()]

def get_surplus(prog, deg, rel, n=8):
    ps = get_program_skills(prog, deg)
    rc = get_role_counter(rel)
    return sorted(ps - set(rc.keys()))[:n]

# ─── MATPLOTLIB SETUP ────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

def save_fig(fig, name):
    path = os.path.join(TMPDIR, f"{name}.png")
    fig.savefig(path, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path

# ─── METHODOLOGY DIAGRAM ─────────────────────────────────────────────────────
def make_methodology_diagram():
    fig, ax = plt.subplots(figsize=(13, 3.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.6)
    ax.axis("off")

    def box(cx, cy, w, h, title, sub, fill, edge):
        r = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.07", lw=1.4,
                           facecolor=fill, edgecolor=edge)
        ax.add_patch(r)
        ax.text(cx, cy + (0.16 if sub else 0), title,
                ha="center", va="center", fontsize=8.5, fontweight="bold", color=DARK)
        if sub:
            ax.text(cx, cy - 0.2, sub, ha="center", va="center",
                    fontsize=7, color=MUTED)

    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#94A3B8",
                                   lw=1.5, mutation_scale=13))

    box(1.1, 2.8, 1.7, 1.0, "Course", "Syllabi (YSU)", BLUE_BG, BLUE)
    box(3.3, 2.8, 1.7, 1.0, "Skill", "Extraction (LLM)", GREEN_BG, GREEN)
    box(1.1, 1.0, 1.7, 1.0, "Job Postings", "753 IT roles", ORANGE_BG, ORANGE)
    box(3.3, 1.0, 1.7, 1.0, "Skill", "Extraction (LLM)", GREEN_BG, GREEN)
    box(6.2, 1.9, 2.0, 1.0, "ESCO v1.2", "Normalization", GREEN_BG, GREEN)
    box(9.0, 1.9, 2.0, 1.0, "Semantic", "Matching", ORANGE_BG, ORANGE)
    box(11.6, 1.9, 1.7, 1.0, "Alignment", "Score", BLUE_BG, BLUE)

    arr(1.95, 2.8, 2.45, 2.8)
    arr(1.95, 1.0, 2.45, 1.0)
    arr(4.15, 2.8, 5.2, 2.2)
    arr(4.15, 1.0, 5.2, 1.6)
    arr(7.2, 1.9, 8.0, 1.9)
    arr(10.0, 1.9, 10.75, 1.9)

    plt.tight_layout(pad=0.2)
    return save_fig(fig, "methodology")

# ─── PORTFOLIO CHART ─────────────────────────────────────────────────────────
def make_portfolio_chart():
    rows = []
    for prog, deg in PROGRAM_ORDER:
        r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
        if r.empty: continue
        s = r.iloc[0]["core_role_coverage_pct"]
        if pd.isna(s): continue
        sn = SHORT_NAMES.get(prog, prog[:45])
        rows.append((f"{sn}  ({deg[:2].upper()})", s))
    rows.sort(key=lambda x: x[1])

    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    bar_colors = [score_hex(v) for v in values]
    ysu_mean = alignment["core_role_coverage_pct"].dropna().mean()

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y = list(range(len(labels)))
    bars = ax.barh(y, values, color=bar_colors, height=0.52, edgecolor="none", zorder=3)

    ax.xaxis.grid(True, color="#E2E8F0", lw=0.7, zorder=0)
    ax.set_axisbelow(True)

    ax.axvline(ysu_mean, color=BLUE, ls="--", lw=1.5, alpha=0.85, zorder=4)
    ax.axvline(24.1, color="#94A3B8", ls=":", lw=1.2, alpha=0.9, zorder=4)
    ax.text(ysu_mean + 0.6, len(rows) - 0.6,
            f"YSU mean  {ysu_mean:.1f}%", color=BLUE, fontsize=8, va="top", fontweight="bold")
    ax.text(24.1 + 0.6, 1.0,
            f"National avg  24.1%", color="#94A3B8", fontsize=8, va="bottom")

    for bar, val in zip(bars, values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha="left", fontsize=9,
                color=DARK, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.8)
    ax.set_xlabel("Market alignment score (%)", fontsize=9, color=MUTED, labelpad=8)
    ax.set_xlim(0, max(values) * 1.22)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#E2E8F0")
    ax.tick_params(colors=MUTED)

    legend_patches = [
        mpatches.Patch(color=GREEN,  label="Strong (≥ 50%)"),
        mpatches.Patch(color=TEAL,   label="Good (35–49%)"),
        mpatches.Patch(color=ORANGE, label="Moderate (25–34%)"),
        mpatches.Patch(color=RED,    label="Developing (< 25%)"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8.5,
              framealpha=0.95, edgecolor="#E2E8F0", fancybox=False)

    ax.set_title("YSU IT Programs — Labor Market Alignment",
                 fontsize=13, fontweight="bold", color=DARK, pad=14, loc="left")

    plt.tight_layout()
    return save_fig(fig, "portfolio")


# ─── TOP GAPS CHART ──────────────────────────────────────────────────────────
def make_top_gaps_chart():
    top = (gaps.groupby("gap_skill")["job_frequency"]
           .sum().nlargest(12).reset_index()
           .sort_values("job_frequency"))
    labels = top["gap_skill"].tolist()
    values = top["job_frequency"].tolist()

    fig, ax = plt.subplots(figsize=(11.5, 4.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    clrs = [ORANGE if v >= 300 else (TEAL if v >= 200 else MUTED) for v in values]
    bars = ax.barh(range(len(labels)), values, color=clrs, height=0.52,
                   edgecolor="none", zorder=3, alpha=0.88)

    ax.xaxis.grid(True, color="#E2E8F0", lw=0.7, zorder=0)
    ax.set_axisbelow(True)

    for bar, val in zip(bars, values):
        ax.text(val + 4, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", ha="left", fontsize=8.5, color=DARK)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Job postings requiring this skill (aggregated across all YSU programs)",
                  fontsize=8.5, color=MUTED, labelpad=8)
    ax.set_xlim(0, max(values) * 1.14)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#E2E8F0")
    ax.tick_params(colors=MUTED)
    ax.set_title("Most Frequently Missing Skills Across All YSU Programs",
                 fontsize=11, fontweight="bold", color=DARK, pad=10, loc="left")
    plt.tight_layout()
    return save_fig(fig, "top_gaps")


# ─── REPORTLAB STYLES ────────────────────────────────────────────────────────
def make_styles():
    def ps(name, **kw):
        defaults = dict(fontName="Helvetica", textColor=c(BODY_C), leading=14)
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    return {
        # TOC-tracked headings (names must be H1 / H2 for afterFlowable hook)
        "H1": ps("H1", fontSize=17, fontName="Helvetica-Bold", textColor=c(DARK),
                 spaceBefore=18, spaceAfter=4, leading=22),
        "H2": ps("H2", fontSize=12, fontName="Helvetica-Bold", textColor=c(BLUE),
                 spaceBefore=14, spaceAfter=4, leading=16),
        "h3": ps("h3", fontSize=10, fontName="Helvetica-Bold", textColor=c(DARK),
                 spaceBefore=8, spaceAfter=3, leading=14),

        # Body text
        "body": ps("body", fontSize=9.5, leading=15, alignment=TA_JUSTIFY,
                   spaceAfter=6, textColor=c(BODY_C)),
        "body_sm": ps("body_sm", fontSize=8.5, leading=13, textColor=c(BODY_C), spaceAfter=4),
        "bullet": ps("bullet", fontSize=9.5, leading=15, leftIndent=14, spaceAfter=4,
                     textColor=c(BODY_C), firstLineIndent=-10),

        # Captions / metadata
        "caption": ps("caption", fontSize=7.5, fontName="Helvetica-Oblique",
                      textColor=c(MUTED), alignment=TA_CENTER, spaceAfter=4),
        "meta": ps("meta", fontSize=8, textColor=c(MUTED), spaceAfter=2),

        # Skill text (compact for one-page program sections)
        "sk_match": ps("sk_match", fontSize=8, leading=11, textColor=c(GREEN)),
        "sk_miss":  ps("sk_miss",  fontSize=8, leading=11, textColor=c(RED)),
        "sk_surp":  ps("sk_surp",  fontSize=8, leading=11, textColor=c(MUTED)),
        "sk_cat":   ps("sk_cat",   fontSize=7, fontName="Helvetica-Bold",
                       textColor=c(BLUE), spaceBefore=2, leading=10),

        # Program page heading — no spaceBefore so it sits tight after PageBreak
        "prog_h": ps("prog_h", fontSize=12, fontName="Helvetica-Bold", textColor=c(BLUE),
                     spaceBefore=0, spaceAfter=2, leading=15),

        # Cover
        "cov_uni":   ps("cov_uni",   fontSize=11, textColor=c(MUTED), alignment=TA_CENTER),
        "cov_title": ps("cov_title", fontSize=28, fontName="Helvetica-Bold",
                        textColor=c(DARK), alignment=TA_CENTER, leading=34),
        "cov_sub":   ps("cov_sub",   fontSize=15, textColor=c(MUTED), alignment=TA_CENTER),
        "cov_by":    ps("cov_by",    fontSize=9,  textColor=c(MUTED), alignment=TA_CENTER),
        "cov_name":  ps("cov_name",  fontSize=12, fontName="Helvetica-Bold",
                        textColor=c(DARK), alignment=TA_CENTER),

        # Misc
        "note": ps("note", fontSize=8.5, fontName="Helvetica-Oblique",
                   textColor=c("#7C2D12"), leading=13, leftIndent=6, rightIndent=6),
        "footer": ps("footer", fontSize=7, textColor=c(MUTED), alignment=TA_CENTER),

        # TOC entries
        "toc1": ps("toc1", fontSize=10, leading=18, leftIndent=0, rightIndent=1*cm),
        "toc2": ps("toc2", fontSize=8.5, leading=15, leftIndent=14, textColor=c(MUTED)),
    }

# ─── DOCUMENT TEMPLATE ───────────────────────────────────────────────────────
class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        cover_frame = Frame(MARGIN, MARGIN, W - 2*MARGIN, H - 2*MARGIN,
                            id="cover", showBoundary=0)
        body_frame  = Frame(MARGIN, MARGIN + 0.9*cm, W - 2*MARGIN,
                            H - 2*MARGIN - 0.9*cm, id="body", showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame]),
            PageTemplate(id="Body",  frames=[body_frame], onPage=self._hf),
        ])

    def _hf(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(c(BORDER))
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, H - 1.4*cm, W - MARGIN, H - 1.4*cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(c(MUTED))
        canvas.drawString(MARGIN, H - 1.15*cm,
                          "Yerevan State University  ·  IT Curriculum — Labor Market Alignment  ·  2026")
        canvas.drawRightString(W - MARGIN, H - 1.15*cm, f"Page {doc.page}")
        canvas.line(MARGIN, 1.4*cm, W - MARGIN, 1.4*cm)
        canvas.drawCentredString(W/2, 0.9*cm,
            "Prepared by Liana Aghamalyan  ·  MSc Data Science for Business  ·  YSU 2026  ·  "
            "March 2026 job market data")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = flowable.style.name
            if name == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page, ""))
            elif name in ("H2", "prog_h"):
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page, ""))

# ─── FLOWABLE HELPERS ─────────────────────────────────────────────────────────
def sp(h=0.3): return Spacer(1, h * cm)
def hr(col=BORDER, t=0.6): return HRFlowable(width="100%", thickness=t, color=c(col), spaceBefore=4, spaceAfter=6)

def score_panel(score, n_matched, n_job_skills, n_gaps, n_surplus, doc_score, styles):
    """Clean two-column score display."""
    sh    = score_hex(score)
    sbg   = score_bg(score)
    sl    = score_label(score)
    ss    = f"{score:.1f}%" if score and not np.isnan(score) else "—"
    dq    = "Good" if doc_score >= 0.45 else ("Mixed" if doc_score >= 0.25 else "Limited")
    dq_c  = GREEN if doc_score >= 0.45 else (ORANGE if doc_score >= 0.25 else RED)

    pw = CONTENT_W
    filled = pw * min(max(score or 0, 0), 100) / 100.0
    empty  = pw - filled
    if filled < 4: filled = 4; empty = pw - 4
    if empty  < 0: empty  = 0

    bar = Table([["", ""]], colWidths=[filled, empty])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), c(sh)),
        ("BACKGROUND", (1,0),(1,0), c(BORDER)),
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    score_cell = [
        Paragraph(f'<font size="22" color="{sh}"><b>{ss}</b></font>',
                  ParagraphStyle("sc", fontSize=22, fontName="Helvetica-Bold",
                                 alignment=TA_CENTER, leading=26)),
        Paragraph(f'<font size="9.5" color="{sh}"><b>{sl}</b></font>',
                  ParagraphStyle("sl", fontSize=9.5, fontName="Helvetica-Bold",
                                 alignment=TA_CENTER, leading=13)),
        Paragraph('<font size="7" color="#64748B">market alignment score</font>',
                  ParagraphStyle("sc2", fontSize=7, alignment=TA_CENTER, leading=10,
                                 textColor=c(MUTED))),
    ]
    meta_cell = [
        Paragraph(f"<b>Covered:</b>  {n_matched} of {n_job_skills} skills employers ask for",
                  styles["body_sm"]),
        Paragraph(f"<b>Gaps:</b>  {n_gaps} skills required by employers, not found in syllabi",
                  styles["body_sm"]),
        Paragraph(f"<b>Also taught:</b>  ~{n_surplus} skills in the program, not in job ads",
                  styles["body_sm"]),
        Paragraph(f"<b>Description detail:</b>  {doc_score:.0%}  "
                  f'<font color="{dq_c}"><b>({dq})</b></font>',
                  styles["body_sm"]),
    ]

    panel = Table([[score_cell, meta_cell]],
                  colWidths=[4.2*cm, CONTENT_W - 4.2*cm])
    panel.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("BACKGROUND",   (0,0),(0,0),   c(sbg)),
        ("BACKGROUND",   (1,0),(1,0),   c(BG)),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 10),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LINEABOVE",    (0,0),(-1,0),  1.5, c(sh)),
        ("LINEBELOW",    (0,0),(-1,0),  0.4, c(BORDER)),
        ("LINEBEFORE",   (1,0),(1,0),   0.4, c(BORDER)),
    ]))
    return [panel, bar, sp(0.1)]


def skill_section(matched, missing, surplus_names, styles):
    """Two-column skills breakdown + additional content note."""
    hdr_green = ParagraphStyle("_hg", fontSize=8.5, fontName="Helvetica-Bold",
                               leading=12, spaceAfter=1, textColor=c(GREEN))
    hdr_red   = ParagraphStyle("_hr", fontSize=8.5, fontName="Helvetica-Bold",
                               leading=12, spaceAfter=1, textColor=c(RED))
    caption   = ParagraphStyle("_cap", fontSize=7, fontName="Helvetica-Oblique",
                               textColor=c(MUTED), leading=10, spaceAfter=4)

    m_paras = [
        Paragraph("What this program covers", hdr_green),
        Paragraph("Taught here and in demand by employers", caption),
    ]
    for skill, cnt in matched:
        m_paras.append(Paragraph(f"● {skill}{'  ('+str(cnt)+')' if cnt else ''}",
                                 styles["sk_match"]))
    if not matched:
        m_paras.append(Paragraph("No matched skills found.", styles["body_sm"]))

    g_paras = [
        Paragraph("Gaps to look into", hdr_red),
        Paragraph("Required by employers, not found in syllabi", caption),
    ]
    prev_cat = None
    for item in missing:
        cat = str(item.get("category") or "").strip()
        if cat and cat != prev_cat:
            g_paras.append(Paragraph(f"[ {cat} ]", styles["sk_cat"]))
            prev_cat = cat
        freq = item["job_frequency"]
        fs = f"  ({int(freq)})" if pd.notna(freq) and freq else ""
        g_paras.append(Paragraph(f"● {item['missing_skill']}{fs}", styles["sk_miss"]))
    if not missing:
        g_paras.append(Paragraph("No significant gaps identified.", styles["body_sm"]))

    col_w = (CONTENT_W - 0.2*cm) / 2
    skills_table = Table([[m_paras, g_paras]], colWidths=[col_w, col_w])
    skills_table.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("BACKGROUND",   (0,0),(0,0),   c(GREEN_BG)),
        ("BACKGROUND",   (1,0),(1,0),   c(RED_BG)),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEAFTER",    (0,0),(0,0),   0.4, c(BORDER)),
    ]))

    out = [skills_table]

    if surplus_names:
        examples = ", ".join(surplus_names[:8]) + ("…" if len(surplus_names) > 8 else "")
        surplus_row = Table([[Paragraph(
            f"<b>Also taught (not listed in job ads):</b>  {examples}",
            styles["body_sm"])]],
            colWidths=[CONTENT_W])
        surplus_row.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(0,0), c(BG)),
            ("LEFTPADDING",  (0,0),(0,0), 8),
            ("RIGHTPADDING", (0,0),(0,0), 8),
            ("TOPPADDING",   (0,0),(0,0), 5),
            ("BOTTOMPADDING",(0,0),(0,0), 5),
            ("LINEABOVE",    (0,0),(0,0), 0.4, c(BORDER)),
        ]))
        out.append(surplus_row)

    return out


def interpretation_box(text, gap_type, styles):
    """Shaded interpretation paragraph with gap-type label."""
    interp_style = ParagraphStyle("_is", fontSize=8.5, leading=13,
                                  textColor=c(BODY_C), leftIndent=4, rightIndent=4)
    gt_style = ParagraphStyle("_gt", fontSize=7.5, fontName="Helvetica-Bold",
                               leading=11, textColor=c(TEAL))
    t = Table([[
        Paragraph(text, interp_style),
        Paragraph(f"Gap assessment: {gap_type}", gt_style),
    ]], colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), c(TEAL_BG)),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 10),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LINEBEFORE",   (0,0),(0,-1),  3, c(TEAL)),
        ("LINEBEFORE",   (1,0),(1,-1),  0.4, c(BORDER)),
    ]))
    return t


def actions_box(actions, styles):
    """Compact numbered action items box."""
    act_style = ParagraphStyle("_as", fontSize=8.5, leading=13, textColor=c(BODY_C),
                               leftIndent=14, firstLineIndent=-10, spaceAfter=3)
    hdr_style = ParagraphStyle("_ah", fontSize=8, fontName="Helvetica-Bold",
                               textColor=c(ORANGE), leading=11, spaceAfter=4)
    content = [Paragraph("What to look at first", hdr_style)]
    for i, action in enumerate(actions, 1):
        content.append(Paragraph(f"{i}.  {action}", act_style))
    t = Table([[content]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), c(ORANGE_BG)),
        ("LEFTPADDING",  (0,0),(0,0), 10),
        ("RIGHTPADDING", (0,0),(0,0), 10),
        ("TOPPADDING",   (0,0),(0,0), 7),
        ("BOTTOMPADDING",(0,0),(0,0), 7),
        ("LINEBEFORE",   (0,0),(0,0), 3, c(ORANGE)),
    ]))
    return t


# ─── PER-PROGRAM SECTION ─────────────────────────────────────────────────────
def add_program_section(story, prog, deg, styles, idx):
    print(f"  Program {idx+1}/{len(PROGRAM_ORDER)}: {prog[:55]}…")
    r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
    if r.empty: return
    row = r.iloc[0]

    score      = row.get("core_role_coverage_pct")
    n_matched  = int(row.get("core_n_overlap", 0) or 0)
    n_job_sk   = int(row.get("core_n_job_skills", 0) or 0)
    n_gaps     = int(row.get("core_n_gap", 0) or 0)
    rel        = str(row.get("relevant_roles", ""))
    faculty    = FACULTY_MAP.get((prog, deg), "Yerevan State University")
    doc_score  = get_doc_score(prog, deg)
    sh         = score_hex(score)

    matched  = get_matched(prog, deg, rel, n=12)
    missing  = get_missing(prog, deg, n=12)
    surplus  = get_surplus(prog, deg, rel, n=8)
    n_surp   = len(get_surplus(prog, deg, rel, n=999))

    interpret, gap_type, actions = build_program_narrative(
        prog, deg, score, doc_score, rel, n_gaps, n_matched)

    if idx > 0:
        story.append(PageBreak())

    prog_short = SHORT_NAMES.get(prog, prog)
    story.append(Paragraph(f"{prog_short} — {deg}", styles["prog_h"]))
    url = PROGRAM_URLS.get((prog, deg), "")
    link_suffix = (f'  ·  <link href="{url}" color="{BLUE}">ysu.am program page &gt;&gt;</link>'
                   if url else "")
    story.append(Paragraph(
        f"{faculty}  ·  Yerevan State University{link_suffix}",
        ParagraphStyle("_pm", fontSize=8, textColor=c(MUTED), spaceAfter=2, leading=11)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c(sh),
                             spaceBefore=2, spaceAfter=4))

    for fl in score_panel(score, n_matched, n_job_sk, n_gaps, n_surp, doc_score, styles):
        story.append(fl)

    if rel and rel not in ("unmapped", "nan"):
        story.append(Paragraph(
            f"<b>Target roles:</b>  {rel}",
            ParagraphStyle("rl", fontSize=8, textColor=c(MUTED), spaceAfter=3,
                           leading=11)))

    story.append(sp(0.15))
    story.append(interpretation_box(interpret, gap_type, styles))
    story.append(sp(0.15))

    for fl in skill_section(matched, missing, surplus, styles):
        story.append(fl)

    story.append(sp(0.15))
    story.append(actions_box(actions, styles))


# ─── MAIN PDF BUILD ───────────────────────────────────────────────────────────
def build_pdf():
    styles = make_styles()
    doc = ReportDoc(str(OUT), pagesize=A4,
                    leftMargin=MARGIN, rightMargin=MARGIN,
                    topMargin=MARGIN, bottomMargin=MARGIN)
    story = []

    mapped    = alignment.dropna(subset=["core_role_coverage_pct"])
    ysu_mean  = mapped["core_role_coverage_pct"].mean()
    best_row  = mapped.nlargest(1, "core_role_coverage_pct").iloc[0]
    best_score = best_row["core_role_coverage_pct"]
    best_name  = SHORT_NAMES.get(best_row["program"], best_row["program"])
    n_above    = int((mapped["core_role_coverage_pct"] >= 24.1).sum())

    # ── COVER ────────────────────────────────────────────────────────────────
    story.append(NextPageTemplate("Cover"))
    story.append(sp(3.2))

    story.append(Paragraph("Yerevan State University", styles["cov_uni"]))
    story.append(sp(0.5))
    story.append(Paragraph("IT Curriculum\nLabor Market Alignment",
                            styles["cov_title"]))
    story.append(sp(0.3))
    story.append(Paragraph("Program-by-Program Results  ·  Internal Decision-Support Report",
                            styles["cov_sub"]))
    story.append(sp(0.4))
    story.append(HRFlowable(width="60%", thickness=1, color=c(BORDER),
                             spaceBefore=4, spaceAfter=4, hAlign="CENTER"))
    story.append(sp(1.6))

    def metric_cell(val, label, col):
        return [
            Paragraph(f'<font size="22" color="{col}"><b>{val}</b></font>',
                      ParagraphStyle("mv", fontSize=22, fontName="Helvetica-Bold",
                                     alignment=TA_CENTER, leading=26)),
            Paragraph(label,
                      ParagraphStyle("ml", fontSize=8, textColor=c(MUTED),
                                     alignment=TA_CENTER, leading=12)),
        ]

    cov_data = [[
        metric_cell("13",              "programs analyzed",       DARK),
        metric_cell(f"{ysu_mean:.1f}%","YSU mean alignment",      GREEN),
        metric_cell(f"+{ysu_mean-24.1:.1f}pp", "above national avg (24.1%)", BLUE),
        metric_cell("697",             "courses analyzed",         DARK),
    ]]
    ct = Table(cov_data, colWidths=[4*cm]*4)
    ct.setStyle(TableStyle([
        ("ALIGN",       (0,0),(-1,-1), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0),(-1,-1), 12),
        ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("LINEABOVE",   (0,0),(-1,0),  0.5, c(BORDER)),
        ("LINEBELOW",   (0,0),(-1,0),  0.5, c(BORDER)),
        ("LINEBEFORE",  (1,0),(3,0),   0.5, c(BORDER)),
    ]))
    story.append(ct)
    story.append(sp(2.8))

    story.append(Paragraph("Prepared by", styles["cov_by"]))
    story.append(Paragraph("Liana Aghamalyan", styles["cov_name"]))
    story.append(Paragraph(
        "MSc in Data Science for Business  ·  Advisor: Tigran Karamyan",
        styles["cov_by"]))
    story.append(sp(0.3))
    story.append(Paragraph(
        "Faculty of Economics & Management  ·  Yerevan State University  ·  2026",
        styles["cov_by"]))
    story.append(sp(0.3))
    story.append(Paragraph(
        "Based on 753 IT job postings from 13 sources  ·  Collected March 2026  ·  "
        "Method: LLM + ESCO v1.2 semantic matching",
        ParagraphStyle("cb2", fontSize=7.5, fontName="Helvetica-Oblique",
                       textColor=c(MUTED), alignment=TA_CENTER)))

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())
    story.append(Paragraph("Contents", styles["H1"]))
    story.append(hr())
    story.append(sp(0.3))

    toc = TableOfContents()
    toc.levelStyles = [styles["toc1"], styles["toc2"]]
    toc.dotsMinLevel = 0
    story.append(toc)

    # ── KEY FINDINGS ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Key Findings", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "The four most important things to know from this report.",
        styles["body_sm"]))
    story.append(sp(0.4))

    cw2 = (CONTENT_W - 0.3 * cm) / 2

    def finding_card(title, body_text, title_color, bg_color):
        st_title = ParagraphStyle("_fct", fontSize=9.5, fontName="Helvetica-Bold",
                                  textColor=c(title_color), leading=13, spaceAfter=5)
        st_body  = ParagraphStyle("_fcb", fontSize=8.5, leading=13, textColor=c(BODY_C))
        return [Paragraph(title, st_title), Paragraph(body_text, st_body)]

    card_rows = [
        [
            finding_card(
                "Data programs lead nationally",
                f"{best_name} scores {best_score:.1f}% — 2nd nationally out of 40 mapped "
                "programs across 8 Armenian universities. Applied Statistics & Data Science "
                "MSc reaches 40.6%.",
                GREEN, GREEN_BG,
            ),
            finding_card(
                "Above the national average",
                f"YSU mean {ysu_mean:.1f}% vs. national mean 24.1% — a {ysu_mean-24.1:.1f} pp "
                f"advantage. {n_above} of 13 programs score at or above the national mean.",
                BLUE, BLUE_BG,
            ),
        ],
        [
            finding_card(
                "One gap appears everywhere",
                "Docker, Kubernetes, cloud platforms (AWS/Azure/GCP), and CI/CD pipelines "
                "are missing from every program's syllabi. These practical tools build on "
                "the strong theoretical foundations YSU already provides.",
                ORANGE, ORANGE_BG,
            ),
            finding_card(
                "Gaps are a starting point, not a verdict",
                "Some listed gaps may already be taught in class but not written in "
                "published course descriptions. Always check with faculty before deciding "
                "to change the curriculum.",
                TEAL, TEAL_BG,
            ),
        ],
    ]

    cards_tbl = Table(card_rows, colWidths=[cw2, cw2])
    cards_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), c(GREEN_BG)),
        ("BACKGROUND",    (1,0),(1,0), c(BLUE_BG)),
        ("BACKGROUND",    (0,1),(0,1), c(ORANGE_BG)),
        ("BACKGROUND",    (1,1),(1,1), c(TEAL_BG)),
        ("LINEABOVE",     (0,0),(0,0), 2.5, c(GREEN)),
        ("LINEABOVE",     (1,0),(1,0), 2.5, c(BLUE)),
        ("LINEABOVE",     (0,1),(0,1), 2.5, c(ORANGE)),
        ("LINEABOVE",     (1,1),(1,1), 2.5, c(TEAL)),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LINEBEFORE",    (1,0),(1,-1), 0.3, c(BORDER)),
        ("LINEBELOW",     (0,0),(-1,0), 0.3, c(BORDER)),
    ]))
    story.append(cards_tbl)

    story.append(sp(0.5))
    print("Generating top gaps chart…")
    gaps_path = make_top_gaps_chart()
    story.append(Image(gaps_path, width=CONTENT_W, height=6.0*cm))
    story.append(Paragraph(
        "Figure 1. The skills most often required by Armenian IT employers that are missing "
        "from YSU course descriptions. Count = number of job postings mentioning that skill.",
        styles["caption"]))

    # ── PURPOSE AND SCOPE ────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Purpose and Scope", styles["H1"]))
    story.append(hr())

    story.append(Paragraph(
        "This report shows how well YSU's IT programs match what Armenian employers "
        "currently ask for. It is written for academic leadership — vice-rectors, "
        "curriculum committees, and program directors — to help with curriculum review.",
        styles["body"]))

    story.append(Paragraph("What this report covers", styles["H2"]))
    story.append(Paragraph(
        f"We looked at {len(curriculum):,} courses across 13 YSU IT programs and compared "
        f"what skills they cover against what employers ask for. The employer data comes from "
        f"{meta['job_snapshot']['n_it_postings']:,} IT job postings collected from "
        f"{meta['job_snapshot']['n_sources']} sources in March 2026.",
        styles["body"]))

    story.append(Paragraph("What this report does not do", styles["H2"]))
    for item in [
        "It does not say a program is good or bad — scores are a starting point for conversation",
        "It does not measure how well graduates find jobs or perform at work",
        "It can miss skills that are taught in class but not written in published descriptions",
        "It does not cover the Blockchain and Digital Currencies program "
        "(see end of Section 5 for the reason)",
    ]:
        story.append(Paragraph(f"● {item}", styles["bullet"]))

    story.append(sp(0.3))
    story.append(Paragraph("Important: what these numbers are based on", styles["H2"]))

    baseline_box = Table([[Paragraph(
        "All scores are based on a specific snapshot: published course descriptions "
        "from the 2025–2026 academic year, and job postings collected in March 2026. "
        "If course descriptions are updated or the job market changes, the scores will "
        "change too. This report is a starting point for review, not a final answer.",
        ParagraphStyle("_bb", fontSize=9, leading=14, textColor=c(DARK),
                       leftIndent=4, rightIndent=4))]],
        colWidths=[CONTENT_W])
    baseline_box.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), c(BLUE_BG)),
        ("LEFTPADDING",  (0,0),(0,0), 12),
        ("RIGHTPADDING", (0,0),(0,0), 12),
        ("TOPPADDING",   (0,0),(0,0), 8),
        ("BOTTOMPADDING",(0,0),(0,0), 8),
        ("LINEBEFORE",   (0,0),(0,0), 3, c(BLUE)),
    ]))
    story.append(baseline_box)

    # ── METHOD IN BRIEF ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("How to Read This Report", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "A short explanation of what the alignment score means and how to use it. "
        "Technical details are in the appendix at the end.",
        styles["body_sm"]))

    story.append(Paragraph("How the score is calculated", styles["H2"]))
    story.append(Paragraph(
        "An AI tool reads every course description and every job posting, and extracts "
        "the skills mentioned in each. It then compares the two lists: what share of the "
        "skills employers ask for in a program's relevant job roles does the program "
        "cover? That share is the alignment score. A program with a 40% score covers "
        "40% of the skills that employers in its target field ask for.",
        styles["body"]))

    story.append(sp(0.3))
    print("Generating methodology diagram…")
    meth_path = make_methodology_diagram()
    story.append(Image(meth_path, width=CONTENT_W, height=3.8*cm))
    story.append(Paragraph(
        "Figure 2. How course descriptions and job postings are compared to calculate an alignment score.",
        styles["caption"]))

    story.append(sp(0.3))
    story.append(Paragraph("What the score means", styles["H2"]))

    band_data = [
        ["Score", "Label", "What it means in practice"],
        ["≥ 50%", "Strong",    "Program covers more than half the skills employers ask for in its target roles"],
        ["35–49%","Good",      "Solid coverage with specific gaps in applied tooling"],
        ["25–34%","Moderate",  "Clear areas for strengthening; theoretical foundations are good"],
        ["< 25%", "Developing","Significant gaps, or the program is compared against all roles at once, "
                               "or the program has an intentional theoretical focus"],
    ]
    bt = Table(band_data, colWidths=[2.3*cm, 2.2*cm, CONTENT_W - 4.5*cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), c(DARK)),
        ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [c(BG), colors.white]),
        ("GRID",       (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("BACKGROUND", (1,1),(1,1), c(GREEN_BG)),
        ("BACKGROUND", (1,2),(1,2), c(TEAL_BG)),
        ("BACKGROUND", (1,3),(1,3), c(ORANGE_BG)),
        ("BACKGROUND", (1,4),(1,4), c(RED_BG)),
    ]))
    story.append(bt)

    story.append(sp(0.5))
    story.append(KeepTogether([
        Paragraph("A lower score is not always a problem", styles["h3"]),
        Paragraph(
            "No program can cover every skill that every employer might ever ask for. "
            "A score of 30–40% means the program covers roughly a third of what employers "
            "in its target field ask for — which is a meaningful result. The goal is to "
            "find where targeted improvements would help most, not to judge programs.",
            styles["body"]),
    ]))

    story.append(sp(0.4))
    story.append(KeepTogether([
        Paragraph("Two kinds of gaps", styles["H2"]),
        Paragraph(
            "When a skill appears in the 'Gaps to look into' column, it could mean one of two things:",
            styles["body"]),
        Paragraph(
            "<b>1.  A real gap</b> — the skill is genuinely not taught. "
            "This would require adding content to the curriculum.",
            styles["bullet"]),
        Paragraph(
            "<b>2.  A description gap</b> — the skill is already taught in class, "
            "but the published course description does not mention it. "
            "The fix here is just to update the description — no curriculum change needed.",
            styles["bullet"]),
        Paragraph(
            "Each program page shows a 'Description detail' indicator. When it is Limited or "
            "Mixed (as it is for most YSU programs), the gap list is probably a mix of both "
            "types — checking with faculty is the right first step before any decisions.",
            styles["body"]),
    ]))

    # ── YSU-WIDE FINDINGS ────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("YSU-Wide Findings", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "All 13 YSU programs, ranked by alignment score. Each program is compared only "
        "against the job roles most relevant to it — not the entire market.",
        styles["body"]))
    story.append(sp(0.3))

    print("Generating portfolio chart…")
    port_path = make_portfolio_chart()
    story.append(Image(port_path, width=CONTENT_W, height=7.5*cm))
    story.append(Paragraph(
        "Figure 3. YSU programs ranked by alignment score (March 2026 job data).",
        styles["caption"]))

    story.append(sp(0.3))
    story.append(Paragraph("What stands out", styles["H2"]))
    for obs in [
        f"<b>YSU is above the national average.</b> YSU mean {ysu_mean:.1f}% vs. "
        "national mean 24.1% — {n_above} of 13 programs score at or above the national level. "
        "Data programs lead the way.".format(n_above=n_above),
        "<b>The same gap appears in every program.</b> Docker, Kubernetes, cloud platforms "
        "(AWS/Azure/GCP), and CI/CD pipelines are missing from every program's syllabi. "
        "These are practical tools that build on foundations YSU already teaches well.",
        "<b>Lower scores are not always a problem.</b> Discrete Math, Numerical Analysis, "
        "and the two Informatics programs have lower scores because they are deliberately "
        "theory-focused — job ads don't capture the value of that kind of education.",
        "<b>The two Informatics tracks are a special case.</b> They are compared against all "
        "IT jobs at once, which makes their scores very low. This is a measurement issue, "
        "not a reflection of program quality.",
    ]:
        story.append(Paragraph(f"● {obs}", styles["bullet"]))

    story.append(sp(0.3))
    story.append(Paragraph("Programs at a glance", styles["H2"]))

    sum_rows = [["#", "Program", "Deg.", "Score", "Band"]]
    for i, (prog, deg) in enumerate(PROGRAM_ORDER, 1):
        r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
        if r.empty: continue
        row = r.iloc[0]
        s = row.get("core_role_coverage_pct")
        sn = SHORT_NAMES.get(prog, prog[:52])
        sum_rows.append([
            str(i),
            Paragraph(sn, ParagraphStyle("st", fontSize=8, fontName="Helvetica", leading=11)),
            deg[:4],
            Paragraph(f'<font color="{score_hex(s)}"><b>{s:.1f}%</b></font>' if pd.notna(s) else "—",
                      ParagraphStyle("sv", fontSize=8.5, fontName="Helvetica-Bold",
                                     alignment=TA_CENTER)),
            Paragraph(f'<font color="{score_hex(s)}">{score_label(s)}</font>',
                      ParagraphStyle("sb", fontSize=8, fontName="Helvetica-Bold")),
        ])

    st_tbl = Table(sum_rows, colWidths=[0.7*cm, CONTENT_W - 6*cm, 1.3*cm, 1.8*cm, 2.2*cm])
    st_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), c(DARK)),
        ("TEXTCOLOR",   (0,0),(-1,0), colors.white),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [c(BG), colors.white]),
        ("GRID",        (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
        ("TOPPADDING",  (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",       (0,0),(0,-1), "CENTER"),
        ("ALIGN",       (3,0),(3,-1), "CENTER"),
    ]))
    story.append(st_tbl)

    # ── PROGRAM-BY-PROGRAM RESULTS ───────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Program-by-Program Results", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Each page shows the alignment score, what it likely means for this specific program, "
        "the top skills covered and top gaps, and 2–3 suggested next steps. "
        "The score panel shows the full gap count; the skill columns show the top 12 "
        "by how often employers ask for them.",
        styles["body_sm"]))
    story.append(sp(0.2))

    for idx, (prog, deg) in enumerate(PROGRAM_ORDER):
        add_program_section(story, prog, deg, styles, idx)

    # Blockchain note — flows naturally after the last program
    story.append(sp(0.8))
    story.append(Paragraph("Blockchain and Digital Currencies — Master's", styles["H2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c(MUTED),
                             spaceBefore=3, spaceAfter=6))
    story.append(Paragraph("Faculty of Economics & Management  ·  15 courses", styles["meta"]))
    story.append(sp(0.2))
    story.append(Paragraph(
        "This program could not be included in the comparison. Blockchain and digital "
        "currency roles are not yet well-defined in standard job-market data, and there "
        "were too few relevant Armenian job postings to make a meaningful comparison. "
        "This is a measurement limitation, not a reflection on the program.",
        styles["body"]))

    # ── LIMITATIONS ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Limitations", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Every measurement has limits. Here is what this analysis can and cannot tell you.",
        styles["body"]))

    limitations = [
        ("This is a snapshot, not a trend",
         "All job postings were collected in March 2026. The job market changes over time — "
         "new tools rise, old ones fade. Scores should be recalculated every year to see "
         "whether alignment is improving or declining."),
        ("Job ads do not capture everything employers value",
         "Employers tend to list specific tools and languages in job postings, but rarely "
         "mention critical thinking, problem solving, or domain expertise — even though these "
         "matter just as much. Programs always teach more than what job ads measure."),
        ("Scores depend on how detailed course descriptions are",
         "If a professor teaches Docker in class but the online syllabus doesn't mention it, "
         "it shows up as a gap. No YSU program reached the 'Good' description detail level — "
         "all are Limited or Mixed. This means most gap lists include a mix of real gaps "
         "and description gaps."),
        ("AI extraction is accurate but not perfect",
         "The AI tool reads descriptions and job postings well in most cases, but it can "
         "occasionally miss a skill or extract it imprecisely. Treat results as directionally "
         "accurate, not as exact counts."),
        ("Some skills fall outside the vocabulary used",
         "A standard European skill vocabulary (ESCO) is used for matching. Very new tools, "
         "blockchain-specific skills, and some Armenia-specific roles are not fully covered. "
         "This may slightly lower scores for programs in fast-moving or niche fields."),
        ("Smaller fields have fewer data points",
         "Hardware, Security, QA, and Mobile have fewer job postings than Backend or Data "
         "roles. Programs in these areas carry more uncertainty. The general direction is "
         "still valid, but exact scores are less reliable."),
        ("Scores measure syllabi, not graduate success",
         "A high score means course descriptions cover what employers ask for — it does not "
         "mean graduates find jobs easily or perform well at work. That kind of evidence "
         "requires graduate surveys and employer feedback."),
    ]

    for title, body in limitations:
        story.append(Paragraph(f"<b>{title}</b>", styles["h3"]))
        story.append(Paragraph(body, styles["body"]))
        story.append(sp(0.1))

    # ── RECOMMENDATIONS ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Recommendations", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Suggested actions, starting with the lowest effort. The first two can be done "
        "within a single semester and cost very little.",
        styles["body"]))

    story.append(sp(0.3))

    # What YSU could do first — callout box
    wf_style = ParagraphStyle("_wf", fontSize=9, leading=14, textColor=c(DARK),
                               leftIndent=14, firstLineIndent=-10, spaceAfter=4)
    wf_hdr   = ParagraphStyle("_wfh", fontSize=10, fontName="Helvetica-Bold",
                               textColor=c(GREEN), leading=14, spaceAfter=6)
    wf_sub   = ParagraphStyle("_wfs", fontSize=8, fontName="Helvetica-Oblique",
                               textColor=c(MUTED), leading=11, spaceAfter=8)
    wf_content = [
        Paragraph("What YSU could do first", wf_hdr),
        Paragraph("Low cost · Near term · Measurable impact", wf_sub),
        Paragraph(
            "1.  <b>Check with faculty (1–2 months):</b> Ask faculty in 2–3 programs to "
            "go through the gap list and say which skills are already taught but not written "
            "in descriptions. Start with Data Science in Business and Applied Statistics "
            "& Data Science — they have the highest scores and clearest starting point.",
            wf_style),
        Paragraph(
            "2.  <b>Update course descriptions (1 semester):</b> Based on faculty input, "
            "update descriptions to name the tools and methods already used in class. "
            "This costs nothing and may close a large number of measured gaps.",
            wf_style),
        Paragraph(
            "3.  <b>Rerun this analysis (1 day):</b> After descriptions are updated, "
            "rerun the analysis to see which gaps remain. This shows the real list — "
            "only what is genuinely missing from the curriculum.",
            wf_style),
        Paragraph(
            "4.  <b>Add targeted content (1 semester to pilot):</b> For gaps confirmed "
            "as real — containerization, cloud platforms, CI/CD — consider short applied "
            "modules in the strongest programs. These tools build directly on what "
            "YSU already teaches.",
            wf_style),
    ]
    wf_box = Table([[wf_content]], colWidths=[CONTENT_W])
    wf_box.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), c(GREEN_BG)),
        ("LEFTPADDING",  (0,0),(0,0), 12),
        ("RIGHTPADDING", (0,0),(0,0), 12),
        ("TOPPADDING",   (0,0),(0,0), 10),
        ("BOTTOMPADDING",(0,0),(0,0), 10),
        ("LINEBEFORE",   (0,0),(0,0), 3, c(GREEN)),
    ]))
    story.append(wf_box)
    story.append(sp(0.5))

    story.append(Paragraph("Longer-term actions", styles["H2"]))

    steps = [
        ("Connect with industry",
         "Medium cost · High impact · Ongoing",
         "Guest lectures, internship partnerships, and supervised projects with local tech "
         "companies give students hands-on experience with the applied tools that syllabi "
         "don't fully cover. The data and software engineering programs are the strongest "
         "candidates to start with."),
        ("Run this analysis every year",
         "Low cost · Ongoing value",
         "Re-running the analysis annually turns this into a living tool for the curriculum "
         "committee. It lets you track whether changes you made actually improved scores, "
         "and whether new market demands are emerging. The underlying system already exists "
         "and can be rerun at low cost."),
        ("Benchmark against other Armenian universities",
         "Medium cost · Strategic value",
         "This study already covers seven other Armenian universities. Extending the report "
         "to include NPUA, RAU, AUA, and others — with their agreement — would create a "
         "national benchmark. YSU could lead this effort and use it in dialogue with "
         "employers and accreditation bodies."),
        ("Track graduate outcomes",
         "Longer-term · High strategic value",
         "The real test of curriculum quality is whether graduates find good jobs and feel "
         "prepared. A simple alumni survey — asking where they work, what they do, and what "
         "skills they had to learn on the job — would give a second, human-level check on "
         "the findings in this report."),
    ]

    for title, cost, body in steps:
        story.append(KeepTogether([
            Paragraph(f"<b>{title}</b>", styles["h3"]),
            Paragraph(f'<font color="{BLUE}"><i>{cost}</i></font>',
                      ParagraphStyle("cc", fontSize=8, fontName="Helvetica-Oblique",
                                     textColor=c(BLUE), spaceAfter=4, leading=12)),
            Paragraph(body, styles["body"]),
            sp(0.15),
        ]))

    # ── TECHNICAL APPENDIX ───────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Technical Appendix", styles["H1"]))
    story.append(hr())

    story.append(Paragraph(
        "Technical details for readers who want to understand the methodology more precisely, "
        "verify the results, or reproduce the analysis.",
        styles["body"]))

    _td = ParagraphStyle("_td", fontSize=8.5, leading=13, textColor=c(BODY_C))
    def td(txt): return Paragraph(txt, _td)

    tech_rows = [
        ["Item", "Detail"],
        ["Run identifier",     meta["run_id"]],
        ["Method",             td("LLM skill extraction · full course descriptions · ESCO v1.2 semantic matching")],
        ["ESCO version",       meta["esco_version"]],
        ["Analysis date",      meta["created_at"]],
        ["Job data",           td(f"{meta['job_snapshot']['n_it_postings']:,} IT postings · {meta['job_snapshot']['n_sources']} sources · Collected {meta['job_snapshot']['collected_at']}")],
        ["Curriculum data",    td(f"{len(curriculum):,} YSU courses · {meta['curriculum_snapshot']['n_universities']} universities total in dataset · "
                               f"{meta['curriculum_snapshot']['n_programs']} programs total · Collected {meta['curriculum_snapshot']['collected_at']}")],
        ["Primary metric",     td("Percentage of ESCO skills required by the role groups most relevant to each program that the program covers")],
        ["Experiments",        td("12 methodological variants were tested (TF-IDF / KeyBERT / LLM × course names only / full descriptions × exact match / semantic match). "
                               "The LLM + full descriptions + semantic matching variant performed best and is used throughout this report. "
                               "The full comparison is available in the research dashboard.")],
        ["YSU national ranking", td(f"Data Science in Business (Master) ranks 2nd nationally out of 40 mapped programs across 8 universities. "
                                 f"YSU mean alignment ({ysu_mean:.1f}%) exceeds the national mean (24.1%).")],
    ]
    tt = Table(tech_rows, colWidths=[4*cm, CONTENT_W - 4*cm])
    tt.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), c(DARK)),
        ("TEXTCOLOR",   (0,0),(-1,0), colors.white),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [c(BG), colors.white]),
        ("GRID",        (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING", (0,0),(-1,-1), 8),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("VALIGN",      (0,0),(-1,-1), "TOP"),
        ("FONTNAME",    (0,0),(0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0,1),(0,-1), c(MUTED)),
    ]))
    story.append(tt)

    story.append(sp(0.6))
    story.append(hr())
    story.append(Paragraph(
        "This report is based on automated NLP analysis of publicly available curriculum and job posting data. "
        "It is intended as decision-support evidence for curriculum review, not as a prescriptive audit or "
        "ranking. Results should be read alongside faculty expertise, program goals, and student outcome data.",
        ParagraphStyle("disc", fontSize=8, fontName="Helvetica-Oblique",
                       textColor=c(MUTED), leading=13, alignment=TA_JUSTIFY)))

    # ── BUILD ────────────────────────────────────────────────────────────────
    print("Building PDF (two-pass for table of contents)…")
    doc.multiBuild(story)
    print(f"Done → {OUT}")
    shutil.rmtree(TMPDIR, ignore_errors=True)


if __name__ == "__main__":
    build_pdf()
