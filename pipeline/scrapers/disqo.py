"""Disqo scraper — Lever public API."""
from __future__ import annotations

import requests

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

LEVER_URL = "https://api.lever.co/v0/postings/disqo"
HEADERS = {"User-Agent": "ThesisResearch/1.0 (Armenian IT curriculum alignment; academic use)"}
RAW_CSV = RAW_DIR / "disqo_jobs_raw.csv"


def _is_armenia(posting: dict) -> bool:
    loc = posting.get("categories", {}).get("location", "") or ""
    text = posting.get("text", "") or ""
    return "armenia" in loc.lower() or "yerevan" in loc.lower() or \
           "armenia" in text.lower() or "yerevan" in text.lower()


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    resp = requests.get(LEVER_URL, headers=HEADERS, params={"mode": "json"}, timeout=20)
    resp.raise_for_status()
    all_jobs = resp.json() if isinstance(resp.json(), list) else resp.json().get("postings", [])

    armenia_jobs = [j for j in all_jobs if _is_armenia(j)]
    new_jobs = [j for j in armenia_jobs if j.get("hostedUrl", "") not in seen_urls]
    print(f"  [disqo] {len(armenia_jobs)} Armenia, {len(new_jobs)} new")

    records = []
    for j in new_jobs:
        lists = j.get("lists", [])
        full_text_parts = [j.get("descriptionPlain") or html_to_text(j.get("description", ""))]
        for lst in lists:
            full_text_parts.append(f"{lst.get('text', '')}:\n" + "\n".join(lst.get("content", [])))
        records.append({
            "source": "disqo",
            "source_url": j.get("hostedUrl", ""),
            "job_title": j.get("text", ""),
            "company_name": "DISQO",
            "location": j.get("categories", {}).get("location", ""),
            "department": j.get("categories", {}).get("department", ""),
            "posting_date": "",
            "full_text": "\n\n".join(filter(None, full_text_parts)).strip(),
        })

    count = append_new_rows(RAW_CSV, records)
    print(f"  [disqo] done — {count} new rows appended")
    return records
