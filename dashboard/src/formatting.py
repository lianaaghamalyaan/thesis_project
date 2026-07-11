import pandas as pd


def score_color(score) -> str:
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return "#9e9e9e"
    if score >= 50:
        return "#2e7d32"
    if score >= 35:
        return "#558b2f"
    if score >= 25:
        return "#f57c00"
    return "#c62828"


def score_label(score) -> str:
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return "No data"
    if score >= 50:
        return "Strong"
    if score >= 35:
        return "Good"
    if score >= 25:
        return "Moderate"
    return "Developing"


def format_score(score) -> str:
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return "—"
    return f"{score:.1f}%"


def score_badge(score) -> str:
    color = score_color(score)
    label = score_label(score)
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:0.85em;font-weight:600">{label}</span>'


def score_interpretation(score, relevant_roles: str) -> str:
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return "No alignment data is available for this program."
    label = score_label(score).lower()
    roles = roles_display(relevant_roles)
    return (
        f"This program covers approximately **{score:.0f}%** of the skills commonly required "
        f"in **{roles}** job postings in the Armenian IT market. "
        f"This represents a **{label}** level of documented alignment."
    )


def roles_display(relevant_roles: str) -> str:
    if not relevant_roles or relevant_roles in ("unmapped", "nan", ""):
        return "general IT"
    parts = [r.strip() for r in str(relevant_roles).split(",")]
    if len(parts) > 3:
        return ", ".join(parts[:3]) + f" and {len(parts) - 3} more role groups"
    return " and ".join(parts) if len(parts) == 2 else ", ".join(parts)


def roles_short(relevant_roles: str) -> str:
    if not relevant_roles or relevant_roles in ("unmapped", "nan", ""):
        return "General IT"
    parts = [r.strip() for r in str(relevant_roles).split(",")]
    if len(parts) > 2:
        return parts[0] + f" +{len(parts)-1}"
    return " / ".join(parts)


GAP_TYPE_ICONS = {
    "curriculum_gap": "🔴",
    "documentation_gap": "🟡",
    "uncertain": "⚪",
}

GAP_TYPE_LABELS = {
    "curriculum_gap": "Likely curriculum gap",
    "documentation_gap": "Possible documentation gap",
    "uncertain": "Unclear",
}

CATEGORY_ICONS = {
    "Data & ML": "🤖",
    "Databases": "🗄️",
    "DevOps & Cloud": "☁️",
    "Other Technical": "🔧",
    "Programming Languages": "💻",
    "Security": "🔒",
    "Software Engineering": "⚙️",
    "Web & Mobile Frameworks": "🌐",
}

REC_ICONS = {
    "documentation": "📝",
    "curriculum": "📖",
    "strategy": "🧭",
    "note": "ℹ️",
}

PRIORITY_COLORS = {
    "high": "#c62828",
    "medium": "#f57c00",
    "info": "#1565c0",
}
