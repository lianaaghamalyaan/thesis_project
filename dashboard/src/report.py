from datetime import date

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from .formatting import roles_display, score_label


def _clean(text) -> str:
    """Core PDF fonts are latin-1 only; drop characters they can't render."""
    if text is None:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")


class _ProgramReportPDF(FPDF):
    def multi_cell(self, *args, **kwargs):
        # Two defensive defaults, both needed:
        # 1. multi_cell(w=0, ...) computes width as "to the right margin from
        #    the current x". Its own default new_x=XPos.RIGHT leaves the
        #    cursor at the right edge after drawing, so the *next* call's
        #    available width collapses toward zero — fpdf2 then either raises
        #    FPDFException (WORD wrap) or spins forever trying to fit a
        #    character into ~0 space (CHAR wrap). Resetting to the left
        #    margin after every call is what multi_cell(w=0) actually needs
        #    to be called repeatedly, which we do throughout this file.
        # 2. wrapmode="CHAR" additionally guards against a single unbroken
        #    token (e.g. a long compound skill name) being wider than the
        #    page — WORD wrap has no fallback for that and raises.
        kwargs.setdefault("new_x", XPos.LMARGIN)
        kwargs.setdefault("new_y", YPos.NEXT)
        kwargs.setdefault("wrapmode", "CHAR")
        return super().multi_cell(*args, **kwargs)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "CurriculumLens - Program Alignment Brief", ln=True)
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Generated {date.today().isoformat()} - CurriculumLens", align="C")


def build_program_pdf(
    *,
    university: str,
    program: str,
    degree: str,
    score,
    relevant_roles: str,
    n_covered: int,
    n_gap: int,
    n_total: int,
    doc_score: float,
    gap_type_label: str,
    strengths: list[dict],
    gaps: list[dict],
    snapshot_date: str,
    benchmark: dict | None = None,
) -> bytes:
    pdf = _ProgramReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, _clean(program))
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 6, _clean(f"{degree} - {university}"), ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(20, 20, 20)
    score_text = f"{score:.1f}%" if score is not None else "N/A"
    pdf.cell(0, 14, _clean(f"{score_text}  ({score_label(score)})"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        0,
        6,
        _clean(
            f"Core role-aware coverage for roles: {roles_display(relevant_roles)}. "
            f"Covers {n_covered} of {n_total} core role skills; {n_gap} gaps identified."
        ),
    )
    pdf.ln(2)

    if benchmark is not None and score is not None:
        delta = score - benchmark["peer_mean"]
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 7, "How this compares", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(
            0,
            6,
            _clean(
                f"Peer average across {benchmark['peer_n']} comparable programs at other "
                f"universities (matched by {benchmark['matched_on']}): {benchmark['peer_mean']:.1f}%. "
                f"This program is {'above' if delta >= 0 else 'below'} that average by "
                f"{abs(delta):.1f} points."
            ),
        )
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 7, "Documentation quality", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        0,
        6,
        _clean(
            f"Documentation confidence score: {doc_score:.0%}. "
            f"Gap classification for this program: {gap_type_label}. "
            "A low score here means some listed gaps may reflect thin course "
            "descriptions rather than a true curriculum gap."
        ),
    )
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Top Strengths", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    if strengths:
        for item in strengths[:10]:
            line = f"- {item['skill']}"
            if item.get("job_count"):
                line += f" ({item['job_count']} job postings)"
            pdf.multi_cell(0, 6, _clean(line))
    else:
        pdf.multi_cell(0, 6, "No strengths data available.")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Top Gaps", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    if gaps:
        for g in gaps[:15]:
            line = f"- {g['skill']}"
            if g.get("job_frequency"):
                line += f" ({int(g['job_frequency'])} job postings)"
            pdf.multi_cell(0, 6, _clean(line))
    else:
        pdf.multi_cell(0, 6, "No significant gaps identified.")
    pdf.ln(4)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        5,
        _clean(
            f"Based on a job market snapshot collected {snapshot_date}. Scores reflect "
            "documented curriculum content matched against market-demanded skills; see the "
            "'How it works' page for full methodology."
        ),
    )

    return bytes(pdf.output())
