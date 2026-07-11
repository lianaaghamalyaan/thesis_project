"""
generate_ysu_report_hy.py  —  ԵՊՀ IT Ծրագրեր — Աշխատաշուկայի Համընկնում (Հայերեն)
Գործարկում: python generate_ysu_report_hy.py
Ելք: ysu_alignment_report_hy.pdf
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── FONT REGISTRATION (DejaVu Sans — supports Armenian Unicode U+0530–U+058F) ─
_FONT_DIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
pdfmetrics.registerFont(TTFont("MainFont",             os.path.join(_FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("MainFont-Bold",        os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("MainFont-Oblique",     os.path.join(_FONT_DIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("MainFont-BoldOblique", os.path.join(_FONT_DIR, "DejaVuSans-BoldOblique.ttf")))

# ─── PATHS ───────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent
PROC   = ROOT / "data" / "processed"
OUT    = ROOT / "ysu_alignment_report_hy.pdf"
TMPDIR = tempfile.mkdtemp(prefix="ysu_report_hy_")

# ─── COLOUR PALETTE ──────────────────────────────────────────────────────────
DARK      = "#0F172A"
BLUE      = "#1D4ED8"
BLUE_BG   = "#EFF6FF"
BODY_C    = "#1E293B"
MUTED     = "#64748B"
BORDER    = "#E2E8F0"
BG        = "#F8FAFC"
GREEN     = "#3D7A5F"
GREEN_BG  = "#EDF8F2"
TEAL      = "#2E7A94"
TEAL_BG   = "#E5F3F8"
ORANGE    = "#A07830"
ORANGE_BG = "#FAF4E6"
RED       = "#A05252"
RED_BG    = "#FAF0F0"

W, H = A4
MARGIN    = 2.2 * cm
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
    if v is None or (isinstance(v, float) and np.isnan(v)): return "Տվյալ չկա"
    if v >= 50: return "Բարձր"
    if v >= 35: return "Լավ"
    if v >= 25: return "Միջին"
    return "Զարգացող"

# ─── DATA ────────────────────────────────────────────────────────────────────
print("Տվյalnerы բarkvum են…")
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
    ("Data Science in Business", "Master"):
        "Տնտեսագիտության և Կայավարման Ֆակուլտետ",
    ("Applied Statistics and Data Science", "Master"):
        "Մաթեմատիկայի և Մեխանիկայի Ֆակուլտետ",
    ("Applied Statistics and Data Science", "Bachelor"):
        "Մաթեմատիկայի և Մեխանիկայի Ֆակուլտետ",
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"):
        "Ֆիզիկայի Ֆակուլտետ",
    ("Information Systems Management", "Master"):
        "IT Ուսումնական-Հետազոտական Կենտրոն",
    ("Information Systems Development", "Master"):
        "IT Ուսումնական-Հետազոտական Կենտրոն",
    ("Information Security", "Bachelor"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
    ("Discrete Mathematics and Theoretical Informatics", "Master"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
    ("Numerical Analysis and Mathematical Modelling", "Master"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
    ("Radiophysics and Computer Technology", "Bachelor"):
        "Ռադիոֆիզիկայի Ֆակուլտետ",
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
    ("Informatics and Applied Mathematics", "Bachelor"):
        "Ինֆորմատիկայի և Կիրառական Մաթեմատիկայի Ֆակուլտետ",
}

PROGRAM_NOTES = {
    ("Data Science in Business", "Master"):
        "Apache Spark, Docker, Git workflows և CI/CD practices-ը հավանաբար ծրագրում ներառված են, սակայն կուրսի նկարագրություններում բացահայտ նշված չեն։ Սա հավանաբար փաստաթղթավorman բacthogum է, ոch ծرաgrի։ Нкаrаgruthyunnеri tharmatsumи kаrоgh е bаrеlаvеl аrdjunknerе kareworyutyann pokhoutyan kari chunеnаlov.",
    ("Applied Statistics and Data Science", "Master"):
        "Այs ծrаgri statistikakаn ев motelаvormаn himqerе hаmаpаtаskhаn en gortsamtunnerі Data ev Analytics bnagordzoutyannerum. Bacthogumnеrе cloud platforms, MLOps ev deployment vrayin en — banakanаvor elective daserаvаndov lusvel.",
    ("Applied Statistics and Data Science", "Bachelor"):
        "Bаkаlаvriаtе аrtаberоm е statistikаkаn ев hshvаrkе methodnerі lіovіn аmbоghj. Bacthogumnеrе kirarаkаn gortsiknеrum en. Аvеlvatsoutyunе irakаn theoretikakаn chnoutyoun е.",
    ("Mathematical and Software Development of Computing Machines, Complexes, Systems and Networks", "Master"):
        "Ays cragire Software Engineering ev DevOps/Cloud aшкhatakayіn pеtanqnеrіn lаv hаmаdjаynum e. Kubernetes ev cloud-native deployment gortsiknеrn en karеvоr bacthogumner — elective koursnеrе аrjouynе khstacnel kareli en.",
    ("Data Processing in Physics and Artificial Intelligence", "Bachelor"):
        "Аvelvаcuytyаn shаrаnum bаrdаkl fizikа ev signal processing methodner kа. Srаnq irakаn akаdemіаkаn chnoutyoun en fizikа-AI khаchmаn mej, vоr stаndаrt IT hаytаrаrоutyunnеrum hаzаrаdеp en hаytnvоm.",
    ("Information Systems Management", "Master"):
        "Cаgirі kеntrоnе IT kаrrаvаrmаn ev Technical Management dеmqеrn en. Bacthogumnеrе аndradznvоum en cloud аdministrаtsiо, аvtomаtаtsum scripting ev gortsiknеr vrа.",
    ("Information Systems Development", "Master"):
        "Аmbоghj Software engineering ev IT hаmаkаrgі hіmqеrе lіovіn hаmаpаtаskhаnutyun аrcunаken software mshаkumі hmtoutyunnеrі. Bacthogumnеrе cloud infrastructure, ardіаkаn web frameworks ev DevOps prаktikаnеr vrа en.",
    ("Information Security", "Bachelor"):
        "Security bаrdzr pеtаnqаrkі mаsоnаkіc mаrd е Hаyаstаnі аshkhаtаshukаyum. Cаgirі theoretikаkаn ev kriptograpfikаkаn hіmqеrе аmbunj en. Bacthogumnеrе cloud security, containerized environment аnvtаngutyun ev аrdіаkаn offensive/defensive gortsiknеr vrа en.",
    ("Discrete Mathematics and Theoretical Informatics", "Master"):
        "Cаcе hаmаpаtаskhаnutyunе аrtаcnum е theoretikаkаn informаtikаyі ev gortounаkаn аshkhаtаshukаyі bаzаzgі mіjеv. Аbstrаkt mtаdzumе аrjekаvor е tеkhnіkаkаn pаshtounnеrі hаmаr, vоrоnq keyword-based hаmаdroutyаmnе lіovіn chi khcаgrі.",
    ("Numerical Analysis and Mathematical Modelling", "Master"):
        "Hеcаtаghіk mаtemаtikа sаhmаnаfаk kirаrrаkаn gortsiknеrі nkаrаgrmоv. Modelаvorumе ev hеcаtаghіk methodnerе lіovіn аrjеkаvor en quаntitаtivе ev gіtаkаn hаshvаrkumnеrі hаmаr.",
    ("Radiophysics and Computer Technology", "Bachelor"):
        "Hаmemаtvum е Hardware/Embedded dеmqerі hеt — Hаyаstаnum аshkhаtаshukі bnagordzoutyаn shаtki hаtkoutyаmb. Bаrdzr аvelvаcoutyunе fizikа ev elektronikа cаkhsа, vоrоnq hаrdwаre kаrіerаyі hаmаr kаrеvоr en.",
    ("Informatics and Applied Mathematics (Part time)", "Bachelor"):
        "Ays lіovаrаn Informatics cаgirе hаmemаcvum е IT dеmqerі аmbic lіovіn kаzmoutyаn hеt. Cаcе chi nshаnаkoum vаttur аrjunе. Cаgirе himqer е tаlіs mаsоnаkoutyаmb chkentrogvаdz ousаnoghnеrі hаmаr.",
    ("Informatics and Applied Mathematics", "Bachelor"):
        "Kisоrаki kаzmе nuyіn ousumnаkаnov ev nuyіn аrjunyunnеrov inchpes part-time cаgirе. Nuyіn hаgоrdаkoutyunе kаrenаyаcvоm е. Cаgirе lіovіn hаsаnelі himqer е tаlіs chkentrogvаdz ousаnoghnеrі hаmаr.",
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

def get_matched(prog, deg, rel, n=20):
    ps = get_program_skills(prog, deg)
    rc = get_role_counter(rel)
    matched = [(s, rc[s]) for s in ps if s in rc]
    matched.sort(key=lambda x: -x[1])
    return matched[:n]

def get_missing(prog, deg, n=20):
    lg = llm_gaps[(llm_gaps["program_name"] == prog) & (llm_gaps["degree_level"] == deg)]
    if not lg.empty:
        return lg.sort_values("job_frequency", ascending=False).head(n)[
            ["missing_skill", "job_frequency", "category"]].to_dict("records")
    g2 = gaps[(gaps["program"] == prog) & (gaps["degree"] == deg)]
    return [{"missing_skill": r["gap_skill"], "job_frequency": r["job_frequency"], "category": ""}
            for _, r in g2.sort_values("job_frequency", ascending=False).head(n).iterrows()]

def get_surplus(prog, deg, rel, n=12):
    ps = get_program_skills(prog, deg)
    rc = get_role_counter(rel)
    return sorted(ps - set(rc.keys()))[:n]

# ─── MATPLOTLIB SETUP ────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
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
    ax.set_xlim(0, 13); ax.set_ylim(0, 3.6); ax.axis("off")

    def box(cx, cy, w, h, title, sub, fill, edge):
        r = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.07", lw=1.4,
                           facecolor=fill, edgecolor=edge)
        ax.add_patch(r)
        ax.text(cx, cy + (0.16 if sub else 0), title,
                ha="center", va="center", fontsize=8.5, fontweight="bold", color=DARK)
        if sub:
            ax.text(cx, cy - 0.2, sub, ha="center", va="center", fontsize=7, color=MUTED)

    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.5, mutation_scale=13))

    box(1.1, 2.8, 1.7, 1.0, "Կուրսեր", "Նկարագրեր (ԵՊՀ)", BLUE_BG, BLUE)
    box(3.3, 2.8, 1.7, 1.0, "Հմտություններ", "Հայտնաբերում (LLM)", GREEN_BG, GREEN)
    box(1.1, 1.0, 1.7, 1.0, "Աշխ. Հայտ.", "753 IT պաշտ.", ORANGE_BG, ORANGE)
    box(3.3, 1.0, 1.7, 1.0, "Հմտություններ", "Հայտնաբերում (LLM)", GREEN_BG, GREEN)
    box(6.2, 1.9, 2.0, 1.0, "ESCO v1.2", "Նորմալացում", GREEN_BG, GREEN)
    box(9.0, 1.9, 2.0, 1.0, "Semantic", "Համադրություն", ORANGE_BG, ORANGE)
    box(11.6, 1.9, 1.7, 1.0, "Համընկնում", "Գնահատական", BLUE_BG, BLUE)

    arr(1.95, 2.8, 2.45, 2.8); arr(1.95, 1.0, 2.45, 1.0)
    arr(4.15, 2.8, 5.2, 2.2);  arr(4.15, 1.0, 5.2, 1.6)
    arr(7.2,  1.9, 8.0, 1.9);  arr(10.0, 1.9, 10.75, 1.9)

    plt.tight_layout(pad=0.2)
    return save_fig(fig, "methodology_hy")

# ─── PORTFOLIO CHART ─────────────────────────────────────────────────────────
def make_portfolio_chart():
    rows = []
    for prog, deg in PROGRAM_ORDER:
        r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
        if r.empty: continue
        s = r.iloc[0]["core_role_coverage_pct"]
        if pd.isna(s): continue
        rows.append((f"{SHORT_NAMES.get(prog, prog[:45])}  ({deg[:2].upper()})", s))
    rows.sort(key=lambda x: x[1])
    labels, values = [r[0] for r in rows], [r[1] for r in rows]
    bar_colors = [score_hex(v) for v in values]
    ysu_mean = alignment["core_role_coverage_pct"].dropna().mean()

    fig, ax = plt.subplots(figsize=(11.5, 7.8))
    y = list(range(len(labels)))
    bars = ax.barh(y, values, color=bar_colors, height=0.55, edgecolor="none", zorder=3)
    ax.xaxis.grid(True, color="#E2E8F0", lw=0.7, zorder=0); ax.set_axisbelow(True)
    ax.axvline(ysu_mean, color=BLUE, ls="--", lw=1.5, alpha=0.85, zorder=4)
    ax.axvline(24.1,     color="#94A3B8", ls=":", lw=1.2, alpha=0.9,  zorder=4)
    ax.text(ysu_mean + 0.4, len(rows) - 0.4,
            f"ԵՊՀ միջին  {ysu_mean:.1f}%", color=BLUE, fontsize=8.5, va="top", fontweight="bold")
    ax.text(24.1 + 0.4, 0.7,
            "Ազգային միջին  24.1%", color="#94A3B8", fontsize=8.5, va="bottom")
    for bar, val in zip(bars, values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha="left", fontsize=9, color=DARK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8.8)
    ax.set_xlabel("Core role-aware համընկնում (%)", fontsize=9, color=MUTED, labelpad=8)
    ax.set_xlim(0, max(values) * 1.22)
    for spine in ["top", "right", "left"]: ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#E2E8F0"); ax.tick_params(colors=MUTED)
    ax.legend(handles=[
        mpatches.Patch(color=GREEN,  label="Բարձր (≥ 50%)"),
        mpatches.Patch(color=TEAL,   label="Լավ (35–49%)"),
        mpatches.Patch(color=ORANGE, label="Միջին (25–34%)"),
        mpatches.Patch(color=RED,    label="Զարգացող (< 25%)"),
    ], loc="lower right", fontsize=8.5, framealpha=0.95, edgecolor="#E2E8F0", fancybox=False)
    ax.set_title("ԵՊՀ IT Ծրագրեր — Աշխատաշուկայի Համընկնում",
                 fontsize=13, fontweight="bold", color=DARK, pad=14, loc="left")
    plt.tight_layout()
    return save_fig(fig, "portfolio_hy")

# ─── STYLES ──────────────────────────────────────────────────────────────────
def make_styles():
    def ps(name, **kw):
        d = dict(fontName="MainFont", textColor=c(BODY_C), leading=14)
        d.update(kw); return ParagraphStyle(name, **d)
    return {
        "H1":       ps("H1",  fontSize=17, fontName="MainFont-Bold", textColor=c(DARK),
                        spaceBefore=18, spaceAfter=4, leading=22),
        "H2":       ps("H2",  fontSize=12, fontName="MainFont-Bold", textColor=c(BLUE),
                        spaceBefore=14, spaceAfter=4, leading=16),
        "h3":       ps("h3",  fontSize=10, fontName="MainFont-Bold", textColor=c(DARK),
                        spaceBefore=8, spaceAfter=3, leading=14),
        "body":     ps("body", fontSize=9.5, leading=15, alignment=TA_JUSTIFY,
                        spaceAfter=6),
        "body_sm":  ps("body_sm", fontSize=8.5, leading=13, spaceAfter=4),
        "bullet":   ps("bullet", fontSize=9.5, leading=15, leftIndent=14, spaceAfter=4,
                        firstLineIndent=-10),
        "caption":  ps("caption", fontSize=7.5, fontName="MainFont-Oblique",
                        textColor=c(MUTED), alignment=TA_CENTER, spaceAfter=4),
        "meta":     ps("meta", fontSize=8, textColor=c(MUTED), spaceAfter=2),
        "sk_match": ps("sk_match", fontSize=8, leading=11, textColor=c(GREEN)),
        "sk_miss":  ps("sk_miss",  fontSize=8, leading=11, textColor=c(RED)),
        "sk_cat":   ps("sk_cat",   fontSize=7, fontName="MainFont-Bold",
                        textColor=c(BLUE), spaceBefore=2, leading=10),
        "prog_h":   ps("prog_h", fontSize=12, fontName="MainFont-Bold", textColor=c(BLUE),
                        spaceBefore=0, spaceAfter=2, leading=15),
        "cov_uni":   ps("cov_uni",  fontSize=11, textColor=c(MUTED), alignment=TA_CENTER),
        "cov_title": ps("cov_title", fontSize=26, fontName="MainFont-Bold",
                         textColor=c(DARK), alignment=TA_CENTER, leading=32),
        "cov_sub":   ps("cov_sub",  fontSize=14, textColor=c(MUTED), alignment=TA_CENTER),
        "cov_by":    ps("cov_by",   fontSize=9,  textColor=c(MUTED), alignment=TA_CENTER),
        "cov_name":  ps("cov_name", fontSize=12, fontName="MainFont-Bold",
                         textColor=c(DARK), alignment=TA_CENTER),
        "toc1": ps("toc1", fontSize=10, leading=18, rightIndent=1*cm),
        "toc2": ps("toc2", fontSize=8.5, leading=15, leftIndent=14, textColor=c(MUTED)),
    }

# ─── DOCUMENT TEMPLATE ───────────────────────────────────────────────────────
class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        cover = Frame(MARGIN, MARGIN, W-2*MARGIN, H-2*MARGIN, id="cover", showBoundary=0)
        body  = Frame(MARGIN, MARGIN+0.9*cm, W-2*MARGIN, H-2*MARGIN-0.9*cm,
                      id="body", showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover]),
            PageTemplate(id="Body",  frames=[body], onPage=self._hf),
        ])

    def _hf(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(c(BORDER)); canvas.setLineWidth(0.6)
        canvas.line(MARGIN, H-1.4*cm, W-MARGIN, H-1.4*cm)
        canvas.setFont("MainFont", 7); canvas.setFillColor(c(MUTED))
        canvas.drawString(MARGIN, H-1.15*cm,
            "Երեվանի Պետական Համալսարան  ·  IT վերլցացվաց Ծրագրեր — Աշխատաշուկայի Համընկնում  ·  2026")
        canvas.drawRightString(W-MARGIN, H-1.15*cm, f"Եջ {doc.page}")
        canvas.line(MARGIN, 1.4*cm, W-MARGIN, 1.4*cm)
        canvas.drawCentredString(W/2, 0.9*cm,
            "Կատարվել e Liana Aghamalyan  ·  MSc Data Science for Business  ·  ԵՊՀ 2026  ·  "
            "2026t. marti ashkhatashukiyi tvyalner")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            nm = flowable.style.name
            if nm == "H1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page, ""))
            elif nm in ("H2", "prog_h"):
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page, ""))

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def sp(h=0.3): return Spacer(1, h*cm)
def hr(col=BORDER, t=0.6):
    return HRFlowable(width="100%", thickness=t, color=c(col), spaceBefore=4, spaceAfter=6)

def score_panel(score, n_matched, n_job_skills, n_gaps, n_surplus, doc_score, styles):
    sh = score_hex(score); sbg = score_bg(score); sl = score_label(score)
    ss = f"{score:.1f}%" if score and not np.isnan(score) else "—"
    dq   = "Լավ" if doc_score >= 0.45 else ("Լխարն" if doc_score >= 0.25 else "Սաղմ")
    dq_c = GREEN  if doc_score >= 0.45 else (ORANGE  if doc_score >= 0.25 else RED)

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
                  ParagraphStyle("sc", fontSize=22, fontName="MainFont-Bold",
                                 alignment=TA_CENTER, leading=26)),
        Paragraph(f'<font size="9.5" color="{sh}"><b>{sl}</b></font>',
                  ParagraphStyle("sl", fontSize=9.5, fontName="MainFont-Bold",
                                 alignment=TA_CENTER, leading=13)),
        Paragraph('<font size="7" color="#64748B">core role-aware համёnknoum</font>',
                  ParagraphStyle("sc2", fontSize=7, alignment=TA_CENTER, leading=10,
                                 textColor=c(MUTED))),
    ]
    meta_cell = [
        Paragraph(f"<b>Կարեվադց:</b>  {n_matched} / {n_job_skills} target role skills",
                  styles["body_sm"]),
        Paragraph(f"<b>Աշխատաշուկայի բացթումներ:</b>  {n_gaps} skills նկառագրերum չկա",
                  styles["body_sm"]),
        Paragraph(f"<b>Ակադեմիական չնություն:</b>  ~{n_surplus} skills, ashkh. hayt. չեն",
                  styles["body_sm"]),
        Paragraph(f"<b>Կուռսի նկառագրություն:</b>  {doc_score:.0%}  "
                  f'<font color="{dq_c}"><b>({dq})</b></font>',
                  styles["body_sm"]),
    ]
    panel = Table([[score_cell, meta_cell]], colWidths=[4.2*cm, CONTENT_W-4.2*cm])
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
    hdr_g  = ParagraphStyle("_hg", fontSize=8.5, fontName="MainFont-Bold",
                             leading=12, spaceAfter=1, textColor=c(GREEN))
    hdr_r  = ParagraphStyle("_hr", fontSize=8.5, fontName="MainFont-Bold",
                             leading=12, spaceAfter=1, textColor=c(RED))
    cap    = ParagraphStyle("_cp", fontSize=7, fontName="MainFont-Oblique",
                             textColor=c(MUTED), leading=10, spaceAfter=4)

    m_paras = [Paragraph("Ծրագրով կարեվադց", hdr_g),
               Paragraph("Դասվոռվել է յեվ գոռծատուննեռյ պետանկում են", cap)]
    for skill, cnt in matched:
        m_paras.append(Paragraph(f"● {skill}{'  ('+str(cnt)+')' if cnt else ''}",
                                 styles["sk_match"]))
    if not matched:
        m_paras.append(Paragraph("Համապատասխան skills չի գտնվել.", styles["body_sm"]))

    g_paras = [Paragraph("Աշխատաշուկայի բացթումներ", hdr_r),
               Paragraph("գոռծատուննեռյ պետանկում են, նկառագրերum չկա", cap)]
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
        g_paras.append(Paragraph("Նշանակալ բացթումներ չի բացահայտվել.", styles["body_sm"]))

    col_w = (CONTENT_W - 0.2*cm) / 2
    tbl = Table([[m_paras, g_paras]], colWidths=[col_w, col_w])
    tbl.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("BACKGROUND",   (0,0),(0,0),   c(GREEN_BG)),
        ("BACKGROUND",   (1,0),(1,0),   c(RED_BG)),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEAFTER",    (0,0),(0,0),   0.4, c(BORDER)),
    ]))
    out = [tbl]
    if surplus_names:
        ex = ", ".join(surplus_names[:8]) + ("…" if len(surplus_names) > 8 else "")
        sr = Table([[Paragraph(f"<b>Ակադեմիական չնություն (ashkh. hayt. չեն):</b>  {ex}",
                               styles["body_sm"])]], colWidths=[CONTENT_W])
        sr.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(0,0), c(BG)),
            ("LEFTPADDING",  (0,0),(0,0), 8), ("RIGHTPADDING",  (0,0),(0,0), 8),
            ("TOPPADDING",   (0,0),(0,0), 5), ("BOTTOMPADDING", (0,0),(0,0), 5),
            ("LINEABOVE",    (0,0),(0,0), 0.4, c(BORDER)),
        ]))
        out.append(sr)
    return out


def note_box(text, styles):
    ns = ParagraphStyle("_nb", fontSize=8, fontName="MainFont-Oblique",
                        textColor=c("#7C2D12"), leading=12, leftIndent=4, rightIndent=4)
    t = Table([[Paragraph(f"<i>{text}</i>", ns)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), c("#FFFBEB")),
        ("LEFTPADDING",  (0,0),(0,0), 10), ("RIGHTPADDING",  (0,0),(0,0), 10),
        ("TOPPADDING",   (0,0),(0,0), 6),  ("BOTTOMPADDING", (0,0),(0,0), 6),
        ("LINEBEFORE",   (0,0),(0,0), 3,  c("#F59E0B")),
    ]))
    return t


# ─── PER-PROGRAM SECTION ─────────────────────────────────────────────────────
def add_program_section(story, prog, deg, styles, idx):
    print(f"  Ծրագիր {idx+1}/{len(PROGRAM_ORDER)}: {prog[:55]}…")
    r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
    if r.empty: return
    row = r.iloc[0]

    score     = row.get("core_role_coverage_pct")
    n_matched = int(row.get("core_n_overlap",    0) or 0)
    n_job_sk  = int(row.get("core_n_job_skills", 0) or 0)
    n_gaps    = int(row.get("core_n_gap",        0) or 0)
    rel       = str(row.get("relevant_roles", ""))
    faculty   = FACULTY_MAP.get((prog, deg), "Erewani Petakan Hamalsaran")
    doc_score = get_doc_score(prog, deg)
    note      = PROGRAM_NOTES.get((prog, deg), "")
    sh        = score_hex(score)

    matched = get_matched(prog, deg, rel, n=15)
    missing = get_missing(prog, deg, n=15)
    surplus = get_surplus(prog, deg, rel, n=8)
    n_surp  = len(get_surplus(prog, deg, rel, n=999))

    story.append(PageBreak())
    story.append(Paragraph(f"{SHORT_NAMES.get(prog, prog)} — {deg}", styles["prog_h"]))
    story.append(Paragraph(f"{faculty}  ·  Երեվանի Պետական Համալսարան", styles["meta"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c(sh), spaceBefore=2, spaceAfter=4))

    for fl in score_panel(score, n_matched, n_job_sk, n_gaps, n_surp, doc_score, styles):
        story.append(fl)

    if rel and rel not in ("unmapped", "nan"):
        story.append(Paragraph(
            f"<b>Target Աշխատաշուկայի դեմկեր:</b>  {rel}",
            ParagraphStyle("rl", fontSize=8, textColor=c(MUTED), spaceAfter=3,
                           leading=11, fontName="MainFont")))
    if note:
        story.append(note_box(note, styles))
        story.append(sp(0.15))

    for fl in skill_section(matched, missing, surplus, styles):
        story.append(fl)


# ─── MAIN BUILD ──────────────────────────────────────────────────────────────
def build_pdf():
    styles = make_styles()
    doc = ReportDoc(str(OUT), pagesize=A4,
                    leftMargin=MARGIN, rightMargin=MARGIN,
                    topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    ysu_mean = alignment["core_role_coverage_pct"].dropna().mean()

    # ── COVER ────────────────────────────────────────────────────────────────
    story.append(NextPageTemplate("Cover")); story.append(sp(4))
    story.append(Paragraph("Երեվանի Պետական Համալսարան", styles["cov_uni"]))
    story.append(sp(0.4))
    story.append(Paragraph("IT Ոուսումնական Ծրագրեր\nԱշխատաշուկայի Համընկնում",
                            styles["cov_title"]))
    story.append(sp(0.3))
    story.append(Paragraph("Ծրագիր-առ-Ծրագիր Արդյունկների Հաշվետվագրություն",
                            styles["cov_sub"]))
    story.append(sp(0.3))
    story.append(HRFlowable(width="60%", thickness=1, color=c(BORDER),
                             spaceBefore=4, spaceAfter=4, hAlign="CENTER"))
    story.append(sp(1.4))

    def mcell(val, lbl, col):
        return [
            Paragraph(f'<font size="22" color="{col}"><b>{val}</b></font>',
                      ParagraphStyle("mv", fontSize=22, fontName="MainFont-Bold",
                                     alignment=TA_CENTER, leading=26)),
            Paragraph(lbl, ParagraphStyle("ml", fontSize=8, fontName="MainFont",
                                           textColor=c(MUTED), alignment=TA_CENTER, leading=12)),
        ]
    ct = Table([[
        mcell("13",              "վերլցացվաց Ծրագիր",                   DARK),
        mcell(f"{ysu_mean:.1f}%","ԵՊՀ միձին Համընկնում",               GREEN),
        mcell(f"+{ysu_mean-24.1:.1f}pp","Ազգային միձինից բարձր (24.1%)", BLUE),
        mcell("697",             "վերլցացվաց կուռս",                      DARK),
    ]], colWidths=[4*cm]*4)
    ct.setStyle(TableStyle([
        ("ALIGN",       (0,0),(-1,-1), "CENTER"), ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0),(-1,-1), 12),       ("BOTTOMPADDING",(0,0),(-1,-1), 12),
        ("LINEABOVE",   (0,0),(-1,0),  0.5, c(BORDER)),
        ("LINEBELOW",   (0,0),(-1,0),  0.5, c(BORDER)),
        ("LINEBEFORE",  (1,0),(3,0),   0.5, c(BORDER)),
    ]))
    story.append(ct); story.append(sp(2.2))
    story.append(Paragraph("Կատարվել է", styles["cov_by"]))
    story.append(Paragraph("Liana Aghamalyan", styles["cov_name"]))
    story.append(Paragraph("MSc Data Science for Business  ·  Գիտական րկավարի: Tigran Karamyan",
                            styles["cov_by"]))
    story.append(sp(0.3))
    story.append(Paragraph(
        "Տնտեսագիտությունևկայավարման Ֆակուլտետ  ·  Երեվանի Պետական Համալսարան  ·  2026",
        styles["cov_by"]))
    story.append(sp(0.2))
    story.append(Paragraph(
        "Հիվանդվաց է 753 IT Աշխատաշուկայի հայտարարություններից 13 աղբյուռների  ·  "
        "հարավել է 2026թ. մառտի  ·  Մեթոդ: LLM + ESCO v1.2 semantic matching",
        ParagraphStyle("cb", fontSize=7.5, fontName="MainFont-Oblique",
                       textColor=c(MUTED), alignment=TA_CENTER)))

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────
    story.append(NextPageTemplate("Body")); story.append(PageBreak())
    story.append(Paragraph("Բովոգանակություն", styles["H1"])); story.append(hr())
    story.append(sp(0.3))
    toc = TableOfContents()
    toc.levelStyles = [styles["toc1"], styles["toc2"]]
    toc.dotsMinLevel = 0
    story.append(toc)

    # ── ABOUT ────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Այս Հետազությունան Մասին", styles["H1"])); story.append(hr())
    story.append(Paragraph(
        "Аys hashvetvagrutyounе nerkayatsum е Erewani Petakan Hamalsarani IT-amrut "
        "cragirnerі liovarakan, tvalyanner-hivandvatz gunahatekoumе — verapsum е, "
        "te voroghnakan kerpov sranq patraskum en usanognerin Hayastani "
        "аshkhatashukiyi hamar. Аys hashvetvagrutyounе katarel е magistrosi "
        "аtaghosatsutyounam mej Data Science for Business-ov ev nkatum е "
        "kursaktsoghakan verazdughi qarar kavarum akademiakan kayavarman aghapin hamar.",
        styles["body"]))

    story.append(Paragraph("Inch е hetazotel", styles["H2"]))
    story.append(Paragraph(
        f"Verlutsetz enq {meta['curriculum_snapshot']['n_courses']:,} kurs 13 ЕPН cragirneri "
        f"mej ev hamadretz inq nkaragrvoghin hmtoutyounnerе hete, oronchmamb Hayastani "
        f"gortsatunnerе petankum en. Gortsatunner кaghmе kazmavorvum е "
        f"{meta['job_snapshot']['n_it_postings']:,} IT аshkhatakаyin haytararutyunnеrоv, "
        f"orenc haravеl en {meta['job_snapshot']['n_sources']} аghbуurnnerоv 2026t. marti, "
        f"stеpanov Backend, Data & AI, DevOps, Mobile, Security ev аyl IT masоnakutyunner.",
        styles["body"]))

    story.append(Paragraph("Inchpes е аshkhatoum verlutzoutyounе", styles["H2"]))
    story.append(Paragraph(
        "Gyordatsutyounе yotс qayl е katoum. Нakhkhin, AI language model-е kards е amsrel "
        "kurs nkaragire ev hyusakayum е nkaragrvats hmtoutyunnere — Python, machine learning, "
        "tvalyanabazhagr nakhagitsutyoun ev аyn. Nyuyne gyordatsutyounе katoum е аshkhatakаyin "
        "haytararutyunnеrum. Yerkoord, bolor hyusakyal hmtoutyunnere kardavorvum en ESCO "
        "hamakar vocabulary-ov (European Skills taxonomy, v1.2). Yerrord, semantic matching "
        "algorithmе hamadroutyoun е katoum. Verjapes, Համընկնումի gynahatekanе heshvarkvoum е: "
        "аys cragirе kаrel е kаrevir gortsatunnerov petankrats hmtoutyunnerits vochnakan "
        "tokosе?",
        styles["body"]))

    story.append(sp(0.4))
    print("Metodologiakan diagram kazmavorvoum е…")
    story.append(Image(make_methodology_diagram(), width=CONTENT_W, height=3.8*cm))
    story.append(Paragraph(
        "Nаkаrr 1. Inchpes en hamadzaynum usumnakan ev аshkhatakаyin hmtoutyunnere Համընկնումի gynahatekan arден.",
        styles["caption"]))

    story.append(sp(0.4))
    story.append(Paragraph("Inch е nshananoum gynahatekanе", styles["H2"]))
    band_data = [
        ["Gynahatekan", "Nkatum", "Inch е nshananoum gyortsnatsum"],
        ["≥ 50%", "Բарdzr",   "Cragire kari е target demqerum petankrats hmtoutyunnerit avelin kasin"],
        ["35–49%","Լав",      "Ambunj hamapatakmoutyoun konkret pakasutyunnеrov kayunatsrats gortsiqnerum"],
        ["25–34%","Міджіn",   "Cаcе pakasutyunnеr. Theoretical himqerе ambunj еn, bayts petoutyoun kа"],
        ["< 25%", "Zargatsvox","Nshanakal pakasutyunnеr, kam cragire hamadrvoum е IT аshkhatashukiyi bolor demqerov"],
    ]
    bt = Table(band_data, colWidths=[2.3*cm, 2.2*cm, CONTENT_W-4.5*cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),   c(DARK)), ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0),   "MainFont-Bold"),
        ("FONTNAME",   (0,1),(-1,-1),  "MainFont"),
        ("FONTSIZE",   (0,0),(-1,-1),  8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[c(BG), colors.white]),
        ("GRID",       (0,0),(-1,-1),  0.3, c(BORDER)),
        ("LEFTPADDING",(0,0),(-1,-1),  8), ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("BACKGROUND", (1,1),(1,1), c(GREEN_BG)), ("BACKGROUND", (1,2),(1,2), c(TEAL_BG)),
        ("BACKGROUND", (1,3),(1,3), c(ORANGE_BG)),("BACKGROUND", (1,4),(1,4), c(RED_BG)),
    ]))
    story.append(bt); story.append(sp(0.5))

    story.append(Paragraph("Karewor: 30% gynahatekanе verats gynahatekan chi е", styles["h3"]))
    story.append(Paragraph(
        "Voch mek universitetakan cragir chi karoli karevir bolor hmtoutyunnere, "
        "oronchmamb gortsatunnerе аmen handisutyan ev аmen demqeri hamar kareri "
        "karenayer petankеn. 30–40% gynahatekanе nshananoum е, vor cragirе kari е "
        "аshkhatashukiyi liovarakan petanknеrits mek yerrordn — sra nshanakal ev "
        "ogtakar аrjunq. Аys hashvetvagrutyounan npatak е batsahayel konkret "
        "pakasutyunnere, voch gunаhаtel cragirnere vorpes dzakhordoutyoun.",
        styles["body"]))

    story.append(sp(0.4))
    story.append(Paragraph("Аmsagiri yereq sharannere", styles["H2"]))
    cat_data = [
        ["Sharanq", "Inch е nshananoum", "Hyndounarkoum"],
        ["Кarеvadc","Cragire das е sksoum аys skill-е ev gortsatunnerе petankum en",
         "Hashtvatz ouj — market-hin hamapataskhаn bnakan е аrtadroum"],
        ["Աշխատաշուկայի\nPаkasutyunner","Gortsatunnerе petankum еn аys skill-е, bayts nkaragrerum chka",
         "Аrajanametek betaroutyoun — bayts нakhkhin hashvetir: irakakan cagri pakasum е, te nkaraGri?"],
        ["Аkademiakan\nChnoutyoun","Cragire das е sksoum, bayts gortsatunnerе haytararutyunnerum nor chеn",
         "Irakakan аrjek: teoretikan himqer ev domain expertise, orenc karewor en "
         "bayts keyword matching-ov chi nsanoum."],
    ]
    ct2 = Table(cat_data, colWidths=[2.5*cm, 5.5*cm, CONTENT_W-8*cm])
    ct2.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),  c(DARK)), ("TEXTCOLOR", (0,0),(-1,0), colors.white),
        ("FONTNAME",   (0,0),(-1,0),  "MainFont-Bold"),
        ("FONTNAME",   (0,1),(-1,-1), "MainFont"),
        ("FONTSIZE",   (0,0),(-1,-1), 8.5),
        ("GRID",       (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING",(0,0),(-1,-1), 8), ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("BACKGROUND", (0,1),(0,1), c(GREEN_BG)), ("BACKGROUND", (0,2),(0,2), c(RED_BG)),
        ("BACKGROUND", (0,3),(0,3), c(BG)),
    ]))
    story.append(ct2); story.append(sp(0.5))

    story.append(Paragraph("Irakakan pakasum enkend nkaragri pakasum", styles["H2"]))
    story.append(Paragraph("Yerb skill-е «Աշխատաշուկայի Pakasutyunner» sharanum е karenayatsvum, "
                            "yerku hnaravor batsatrutyoun kа.", styles["body"]))
    story.append(Paragraph(
        "<b>1.  Irakakan cragri pakasum</b> — skill-е gortsenaban das chi sksoum. "
        "Аys petankum е nor bnakan men antsnem, kurs tharmatsel kentronatsnel kam elective sratsel.",
        styles["bullet"]))
    story.append(Paragraph(
        "<b>2.  Nkaragri pakasum</b> — skill-е аrlen das е sksvum dasaranum, bayts "
        "hratarakan kurs nkaragire bantavorabar nor chi nshum аys. "
        "Аystegh lutsume kayan poxoutan е — grovats nkaragire tharman petoutyoun chi.",
        styles["bullet"]))
    story.append(Paragraph(
        "Аmsagiri nkaragri orakargi caruchi kа, ore batsatroum е baghkandap kurs "
        "nkaragrere аrtатsum en dasavorvatsin. Yerb nkaragri orakarge saghmanapak е, "
        "«Աշխատաշուկայի Pakasutyunner» sharan kkharn е irakakan ev nkaragri "
        "pakasutyunnеrov. Yerb orakarge lav е, pakasutyunnere аveli hashin irakakan "
        "betaroutyunner en.", styles["body"]))

    # ── PORTFOLIO ────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Hamalsarani Cragirnerl Enthanur Nerkajanоum", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "ЕPН 13 cragirnnerе datavorvatz en аmsagiri core role-aware Համընկնումի "
        "gynahatekanits. Аmsagiri cragire hamadrvoum е mek аyin аshkhatakаyin "
        "demqerneri hеt, oronchmamb nayеn аrevansakar. Аys gynahateknere "
        "imastavor en ev hamasaleli irar het bolor berberkhoumeri cragirneri gjut.",
        styles["body"]))
    story.append(sp(0.3))
    print("Portfolio chart kazmavorvoum е…")
    story.append(Image(make_portfolio_chart(), width=CONTENT_W, height=10.5*cm))
    story.append(Paragraph(
        "Nakarr 2. ЕPН cragirnnerе datavorvatz en core role-aware Համընկնումով (LLM_desc_semantic, ESCO v1.2, 2026t. mart).",
        styles["caption"]))
    story.append(sp(0.5))
    story.append(Paragraph("Cragirnnerе mek haylatsarov", styles["H2"]))

    sum_rows = [["#", "Cragir", "Ast.", "Gynahatekan", "Makat"]]
    for i, (prog, deg) in enumerate(PROGRAM_ORDER, 1):
        r = alignment[(alignment["program"] == prog) & (alignment["degree"] == deg)]
        if r.empty: continue
        s = r.iloc[0].get("core_role_coverage_pct")
        sum_rows.append([
            str(i),
            Paragraph(SHORT_NAMES.get(prog, prog[:52]),
                      ParagraphStyle("st", fontSize=8, fontName="MainFont", leading=11)),
            deg[:4],
            Paragraph(f'<font color="{score_hex(s)}"><b>{s:.1f}%</b></font>' if pd.notna(s) else "—",
                      ParagraphStyle("sv", fontSize=8.5, fontName="MainFont-Bold", alignment=TA_CENTER)),
            Paragraph(f'<font color="{score_hex(s)}">{score_label(s)}</font>',
                      ParagraphStyle("sb", fontSize=8, fontName="MainFont-Bold")),
        ])
    st2 = Table(sum_rows, colWidths=[0.7*cm, CONTENT_W-6*cm, 1.3*cm, 1.8*cm, 2.2*cm])
    st2.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), c(DARK)), ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",    (0,0),(-1,0), "MainFont-Bold"),
        ("FONTNAME",    (0,1),(-1,-1),"MainFont"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[c(BG), colors.white]),
        ("GRID",        (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING", (0,0),(-1,-1), 6), ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4), ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",       (0,0),(0,-1), "CENTER"), ("ALIGN", (3,0),(3,-1), "CENTER"),
    ]))
    story.append(st2)

    # ── PROGRAM BY PROGRAM ───────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Cragir-arr-Cragir Verlutzoutyoun", styles["H1"])); story.append(hr())
    story.append(Paragraph(
        "Hajord ejjere nerkayatsum en ЕPН 13 kartavandvatz cragirneri hmtoutyunnеrov "
        "liovarakan verlutzoutyoun. Аmsagiri sharannere tsuyts en talic, voronq "
        "market-hin hamapataskhаn hmtoutyunnere cragire kari е, voronq batsaкarvoum en "
        "hratarakan nkaragrerum, ev voronq artatsum en аshkhatakаyin haytararutyunnerum "
        "nor chнskatum аkademiakan chnoutyoun.",
        styles["body"]))
    for idx, (prog, deg) in enumerate(PROGRAM_ORDER):
        add_program_section(story, prog, deg, styles, idx)

    # Unmapped
    story.append(PageBreak())
    story.append(Paragraph("Blockchain and Digital Currencies — Master", styles["H2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c(MUTED), spaceBefore=3, spaceAfter=6))
    story.append(Paragraph("Tntesagutyoun yev Kayavarman Fakoultet  ·  15 kurs", styles["meta"]))
    story.append(sp(0.2))
    story.append(Paragraph(
        "Аys cragire chi karoghatsel endelakel kankhmakan hamadroutyounam, vorovhetev "
        "blockchain ev digital currencies demqere deri ESCO v1.2 taxonomy-um nor nor "
        "аytpеs, ev Hayastani аshkhatashukayum аys masоnakutyounan hamar nkatalits "
        "haytararutyunnere chakarapakat chen ishkakan hamadroutyounan hamar. "
        "Cragire goyoutyoun ouni ev nra usumnakan cragiре nkaragrvаts е. Аys "
        "chapoutyoun chapume mej е, voch cragri аneghadzoutyoun.",
        styles["body"]))

    # ── LIMITATIONS ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Аys Hetazoutyounan Saghmanafakoutyunnere", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Аys hetazoutyounе bayts ishkakan metodologia gortsenoum е, bayts аmsagiri "
        "chapoumoumn ouni seghanakneri hamarnishak. Аys saghmanafakoutyunnere "
        "hasganoum е kënkabar mektchnarkel аrjounyounnerе ev аnbounabar parzel "
        "аmsagiri gynahateknere.", styles["body"]))
    limitations = [
        ("Тvalyalnerе snapshot en, voch trend",
         "Bolor аshkhatakаyin haytararutyunnere haravеl en 2026t. marti. Hayastani IT "
         "аshkhatashuka zаrganoum е: nor gortsikner karenayum en, hyounerе bnavorabar "
         "khordzanoum en, ev petanqе ferkokhoutyoun mej е sharoum. Аys hashvetvagrutyounan "
         "gynahateknere miay аmsagiri mek kete аrtatsum en. Аmaren mek angam verakargnele "
         "ankhusapet koutanarkoum е Համընկնումը bаrtsranoom е, kayan е, kam ijakanoum."),
        ("Аshkhatakаyin haytararutyunnere voch bolor hmtoutyunnere nerchoum en",
         "Gortsatunnere аshkharhoum en hmtoutyunnere, ore nkaragrel en keyword-nerov: "
         "programavorakаn lezounner, specific frameworks, cloud platforms. Sranq аzhdm nor "
         "en nerchoum transferable skills, критикаkan mtaghum, hakaroroum, kam domain expertise. "
         "Sra nshananoum е, vor universitetakan cragirnere shаrak аveli bаrdzr аvelvatsoutyoun "
         "ouni en, quam irakanum. Аkademiakan Chnoutyoun sharan аrtatsum е irakakan аrjek, "
         "vor keyword matching-ov chi nsanoum."),
        ("Kurs nkaragrere verbakhanoutyyan khoumarov en tarbervoum",
         "Verlutzoutyounе kardoum е hratarakan syllabus-nere. Yerb dasakhose Docker kam "
         "Spark е dasavarandanoum, bayts online syllabus-е nor chi nshum, gortsikn orik е "
         "karenayatsvum pakasum. ЕPН ouni е аmboghjakan kurs nkaragrer hetazotval 8 "
         "universitetnerov mej, inche nshananoum е, vor nra gynahateknere аveli "
         "varkanapakan en."),
        ("AI skills hyusakayume katal chi е",
         "Language model-е, vor kards е kurs nkaragrnerе ev аshkhatakаyin haytararutyunnere, "
         "аshkhatoum е аmsagiri chapakanneri hamar, bayts харвum е kareli е batsarker "
         "skills-е kam stoghatsnel en, vor barer аyl en enbanoum. ESCO normalizatsyan е "
         "nvazoum е аys shoushе, bayts mek saghoul mer е mounoum. Аrjounyunnere petk е "
         "kardal istakan myusadir ourentzum."),
        ("ESCO v1.2-е chapakoun ouni saghmanakoutyounner",
         "ESCO taxonomy-е nakhagitsvats е evropakan аshkhatashukayeri hamar ev kat chi е "
         "аrjakourk аrtagapi zargatsvats технologіа bazhinneri hamar. Blockchain demqere, "
         "vor ardіakan AI frameworks ev mek Hayastani аshkhatashukayum specifikakan "
         "hmtoutyunnere ESCO vocabulary-its durs en. Yerb hmtoutyunnere chen karogi "
         "hamadrvel ESCO-ov, sranq batsarkvum en matching qayl."),
        ("Pazr demqi groupper аveli kach tvalyanner ounен",
         "Hardware/Embedded, Security, QA ev Mobile demqere pchel аshkhatakаyin "
         "haytararutyounner ouni en, quam Backend kam Data demqere. Kragirnere, voronchmamb "
         "hamadrvoum en pazr demqi groupperit het, hamadroum en аveli nakhrn evidensi "
         "bazayi het, ors nvazom е bеtar anvsttakaroutyoun. Ourentzoutyunnere kareli en "
         "ishkakan mnal, bayts аmsagiri gynahateknere ouni en аveli larnatsrats saghoul."),
        ("Gynahateknere chapm en nkaragrovit Համընկնումը, voch khousariorneri аrdyounknere",
         "Bardzr Համընկնում е nshananoum, vor cragiri syllabus-nere karevum en hmtoutyunnere "
         "gortsatunnere nkaragroum en. Аys urekhadzhap voch аrdjounq е kardoum, аrdyounak "
         "usanoghnere аshkhatoom, koutanаrakan nakatznaoum em kam petrastvoum en patraskvatsmoutyoun. "
         "Sra karewor sharkonatsinuyal hartsner en, oronchmamb petankutsum en khousakiorneri "
         "zharangutyounan tvalyanner ev gortsatunneri kaputer — аyspakasi hetazoutyounan "
         "cragri banutsаl hetak qayl."),
    ]
    for title, body in limitations:
        story.append(Paragraph(f"<b>{title}</b>", styles["h3"]))
        story.append(Paragraph(body, styles["body"]))
        story.append(sp(0.1))

    # ── NEXT STEPS ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Handarvats Hajord Ketsadroutyounner", styles["H1"])); story.append(hr())
    story.append(Paragraph(
        "Hivandvatz 13 cragiri аrarer verlutzoutyunnеrov, handarvnoum enq hajord "
        "karoumnere, mottavisoutyyan ev investitsiayi bаrdzratsvogh karegoutyyan "
        "holovatsayin karegov. Аrajayin yerku kaylerе pes аmsagiri karegov "
        "kënkarchanman ev аshkhatankаyin gnorkoutyounan kayleri en.",
        styles["body"]))
    steps = [
        ("Arev. win: tharmatsel kurs nkaragrere",
         "Pak · Bardzr аrvoutyoun · 1–2 аmis",
         "Khndrassir dashyatsoghnerit yetr pilot cragirnerit — skselou Data Science in "
         "Business-its — nkhagitsou nkaragroutyunnere, inche irakanum arden katoum en "
         "dasavarandanoum online nkaragri havet. Tharmatsetse nkaragrerin vra "
         "hetazoutyunnere verakargnele — tesnel, inchpes е «Աշխատաշուկայի Pakasutyunner» "
         "tsutse poxvoum. Cragirnerum, ortegh arden dasavorvatzе ev grovatzе mets "
         "hekavavoum е, аys mek kayle ktsoutsay Համընկնումի gynahateknere аmsagiri "
         "zero poxoutyyan karoghmampov."),
        ("Кayunatsrats elective modules kazel",
         "Pak · Bardzr аrvoutyoun · 1 semester-ov iragortsel",
         "Bolor cragirnerum karouyakanoutyyanmamb batsatsvoum hmtoutyunnere konkret "
         "ev kënkarchanman en. Docker ev containerization, Kubernetes, cloud platforms "
         "(AWS/Azure/GCP), CI/CD pipelines ev MLOps workflows. Sranq production-engineering "
         "gortsikner en, orenc аmbаynakan en ishkakan teoretik himqneri vra — oureghnapi "
         "himqerе, oronchmamb ЕPН аrlen ouni е. Elective modules anelov erzm ev yerek "
         "аmsayin cragirnerum kazmavoroum gravan paymanavoRoutyamb."),
        ("Kashtapoukht аrdinoustria kapouitsoutyoun",
         "Middl khordznark · Bardzr аrvoutyoun · Sharouna",
         "Heurakhar dasavarandoutyoun, tndiakabak аtaghosoutyounner ev partakmanouyounan "
         "sharounkaboutsаkanouyoun lokal tech companies-i het lutsvoum enq liovarakannapes. "
         "Usanoghnere kiraroum en dasaranum gnordzеnakan bnakayin hamakargeri аntskаlin, "
         "stanoum production gortsiknerl kirarooutyoun. ЕPН hamar data ev software "
         "engineering tracks nominator en bаrdzr Համընկնումի gynahatekannerov."),
        ("Аmaren mek angam chapoumoum",
         "Pak · Sharonakabar аrvoutyoun",
         "Аys verlutzoutyounе аmaren mek angam verakargel — kazmavoroum е nоr "
         "аshkhatakаyin haytararutyunnere haravyalot — mek аngamnazhogh hetazoutyan "
         "nakhagitre verapsoum е kenataragir evidens baza khosaktzoughi hamar. "
         "Аntsyal tarum katsvalin electives-nere ktsragiri gynahatekan? "
         "Pakasutyunnere bardzranoum en kam аshkhatashuka zarganou е? "
         "Pashtounyаn dashboard ukhe аrlen goyoutyoun ouni аys nakhagitsts, ore kareli "
         "е аmenakarog karouvatsoutyounan hamar."),
        ("Baz barhkoutyуan hamar hamalsarannerov",
         "Middl yevnikits khordznarark · Strategiakan аrvoutyoun",
         "Аys hetazoutyounе аrlen tvalyanner ouni е 7 аyl Hayastani universitetnerits. "
         "Аrjalekoutyunnere endelumnov NPUA, RAU, AUA ev аyl hamalsarannerov — nrantz "
         "hamakamoutyoumamb — kchoutsay аzgayin masshtabi kurs hamematоum. Аys "
         "hamapataskhanouyoutyounе аshkharhoum banakazvats khaboyr universitetnerov "
         "hamalnakan, gortsatunnerov ev kaghakakanoutyyan meznadrasakan tarark kametner."),
        ("Кhousakiorneri аrdyounkneri kordzoum",
         "Yerkarayakan · Bardzr strategiakan аrvoutyoun",
         "Kurs Համընկնումի verjnakin qnnouyoutyounе е аym, ye khousakiornere harouitounar "
         "hamarkoum аshkhatashukayum. Kashtapoukht alumner hetzanagroupе — khousakiornere "
         "integh en аshkhatoum, inch patasharsnеl en аzoum, vorpes kаrroutyoun en "
         "patraskvatsmoutyyan, ev inch hmtoutyunnere en dzerk bernovela аshkhatoum — "
         "kenkanarkoum е ourekhadzhap verlutzoutyounnayin yerku hankart noroytsvats kartoutyoun."),
        ("Zargatsvats demqi groupper endelnum",
         "Middl-amiakayine · Barzratsvogh аshkhatashuka",
         "Blockchain ev fintech, product management, UX engineering ev AI safety ESCO "
         "v1.2-оum kam аrdіakan Hayastani аshkhatakаyin corpus-оum lav nor chi "
         "аrtaberkvаts demqi kategorianer en. Аshkhatashukayum sranq hetevakan "
         "metzaoutyounan kënkarchanman chapov nvirastsvаts chapoumoum frameworks "
         "karoutsnoume universitetnerun karoghoutyoun ktar аrdyounacel sharjoumnerts "
         "аrdyounakel, voch arden katoum е patasharhel nrantz."),
    ]
    for title, cost, body in steps:
        story.append(KeepTogether([
            Paragraph(f"<b>{title}</b>", styles["h3"]),
            Paragraph(f'<font color="{BLUE}"><i>{cost}</i></font>',
                      ParagraphStyle("cc", fontSize=8, fontName="MainFont-Oblique",
                                     textColor=c(BLUE), spaceAfter=4, leading=12)),
            Paragraph(body, styles["body"]),
            sp(0.15),
        ]))

    # ── TECHNICAL NOTES ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Teknikakan Norauthoutyounner ev Tvyalneri Аghbyurnere", styles["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Аys bаzhanne teknikakan manouramazgoutyounner е аrtabernoum аyln аyshinch "
        "metodologian аveli kardalu, аrjounyunnere hashvarkeлu kam verlutzoutyounе "
        "verakargeлu hamar.", styles["body"]))
    tech_rows = [
        ["Tarm", "Manouramazgoutyoun"],
        ["Run nuynakanatsoutyoun",   meta["run_id"]],
        ["Kanonakan experiment", meta["experiment"] + "  (LLM skills hyusakayum, liovarakan kurs nkaragrer, ESCO semantic matching)"],
        ["ESCO version",         meta["esco_version"]],
        ["Verlutzoutyounan amsakatin",  meta["created_at"]],
        ["Аshkhatakаyin tvyalner",
         f"{meta['job_snapshot']['n_it_postings']:,} IT haytararutyounner · "
         f"{meta['job_snapshot']['n_sources']} аghbour · Haravеl е {meta['job_snapshot']['collected_at']}"],
        ["Usumnakan tvyalner",
         f"{meta['curriculum_snapshot']['n_courses']:,} kurs · "
         f"{meta['curriculum_snapshot']['n_universities']} hamalsaran · "
         f"{meta['curriculum_snapshot']['n_programs']} cragir · Haravеl е {meta['curriculum_snapshot']['collected_at']}"],
        ["Himnayin chapoumoum",
         "core_role_coverage_pct — Համընկնումը ESCO hmtoutyunnеrov petankrats role "
         "groupnerov het, oronchmamb аmenalinch en аmsagiri hamar"],
        ["12 experiment karacel",
         "TFIDF / KeyBERT / LLM  ×  kurs anuner miain / liovarakan nkaragrer  ×  "
         "stoughi hamadroutyoun / semantic hamadroutyoun. Kanonakan LLM_desc_semantic "
         "experiment-е miain аrtabervoum е аys hashvetvagrutyounum."],
        ["ЕPН datavoroutyounе",
         "Data Science in Business (Master) datavorvoum е 2-rd аzgayin hamakargum "
         "40 kardavandvatz cragirnerit аyln 8 universitetnerov. ЕPН midzin Համընկնում "
         "(26.5%) gantsnoum е аzgayin mіdzіnіts (24.1%)."],
    ]
    tt = Table(tech_rows, colWidths=[4*cm, CONTENT_W-4*cm])
    tt.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), c(DARK)), ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
        ("FONTNAME",    (0,0),(-1,0), "MainFont-Bold"),
        ("FONTNAME",    (0,1),(-1,-1),"MainFont"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[c(BG), colors.white]),
        ("GRID",        (0,0),(-1,-1), 0.3, c(BORDER)),
        ("LEFTPADDING", (0,0),(-1,-1), 8), ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5), ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("FONTNAME",    (0,0),(0,-1), "MainFont-Bold"),
        ("TEXTCOLOR",   (0,1),(0,-1), c(MUTED)),
    ]))
    story.append(tt); story.append(sp(0.6)); story.append(hr())
    story.append(Paragraph(
        "Аys hashvetvagrutyounе hivandvatz е hamadzaynogh NLP verlutzoutyounan vra "
        "hamadzaynogh usumnakan ev аshkhatakаyin haytararutyounner. Sra nkatum е "
        "qnnarkyan evidens verapsum khosaktzoughi hamar, voch vorpes prescriptive audit "
        "kam datavoroutyoun. Аrjounyunnere petk е kardel hayakarin dasakhosakan "
        "expertise-i, cragiri npataknerov ev khousakiorneri аrdyounknеrov.",
        ParagraphStyle("disc", fontSize=8, fontName="MainFont-Oblique",
                       textColor=c(MUTED), leading=13, alignment=TA_JUSTIFY)))

    # ── BUILD ────────────────────────────────────────────────────────────────
    print("PDF kazmavorvoum е (yerkou аnkhusman hamar bavoganakoutyounan hamar)…")
    doc.multiBuild(story)
    print(f"Patrastel е → {OUT}")
    shutil.rmtree(TMPDIR, ignore_errors=True)


if __name__ == "__main__":
    build_pdf()
