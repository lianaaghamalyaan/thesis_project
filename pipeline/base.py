"""Shared helpers for all scrapers: incremental logic, CSV I/O, text cleaning."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "jobs"


def load_seen_urls(csv_path: Path) -> set[str]:
    """Return the set of source_url values already stored in a raw CSV."""
    if not csv_path.exists():
        return set()
    try:
        df = pd.read_csv(csv_path, usecols=["source_url"], dtype=str)
        return set(df["source_url"].dropna())
    except Exception:
        return set()


def append_new_rows(csv_path: Path, rows: list[dict]) -> int:
    """Append rows to an existing CSV (or create it). Returns count written."""
    if not rows:
        return 0
    df = pd.DataFrame(rows)
    if csv_path.exists():
        df.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(csv_path, index=False, encoding="utf-8")
    return len(rows)


def html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(str(html), "html.parser")
    for tag in soup.find_all(["p", "li", "br", "h1", "h2", "h3", "h4"]):
        tag.insert_before("\n")
    text = soup.get_text(" ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_date(val: str) -> str:
    if not val:
        return ""
    val = val.strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", val)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", val)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return val
