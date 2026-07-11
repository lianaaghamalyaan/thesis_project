"""Picsart scraper — Greenhouse public API, Armenia filter."""
from __future__ import annotations

import requests

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

API_URL = "https://boards-api.greenhouse.io/v1/boards/picsart/jobs"
HEADERS = {"User-Agent": "ThesisResearch/1.0 (Armenian IT curriculum alignment; academic use)"}
RAW_CSV = RAW_DIR / "picsart_jobs_raw.csv"


def _is_armenia(loc: str) -> bool:
    return "armenia" in loc.lower() or "yerevan" in loc.lower()


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    resp = requests.get(API_URL, headers=HEADERS, params={"content": "true"}, timeout=30)
    resp.raise_for_status()
    all_jobs = resp.json().get("jobs", [])

    armenia_jobs = [j for j in all_jobs if _is_armenia(j.get("location", {}).get("name", ""))]
    new_jobs = [j for j in armenia_jobs if j.get("absolute_url", "") not in seen_urls]
    print(f"  [picsart] {len(armenia_jobs)} Armenia, {len(new_jobs)} new")

    records = []
    for j in new_jobs:
        dept = ", ".join(d["name"] for d in j.get("departments", []) if d.get("name"))
        records.append({
            "source": "picsart",
            "source_url": j.get("absolute_url", ""),
            "job_title": j.get("title", ""),
            "company_name": "Picsart",
            "location": j.get("location", {}).get("name", ""),
            "department": dept,
            "posting_date": (j.get("first_published") or "")[:10],
            "full_text": html_to_text(j.get("content", "")),
        })

    count = append_new_rows(RAW_CSV, records)
    print(f"  [picsart] done — {count} new rows appended")
    return records
