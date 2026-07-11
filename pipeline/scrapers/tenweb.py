"""10Web scraper — BambooHR public API."""
from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

BASE = "https://10web.bamboohr.com"
HEADERS = {
    "User-Agent": "ThesisResearch/1.0 (Armenian IT curriculum alignment; academic use)",
    "Accept": "application/json",
}
RAW_CSV = RAW_DIR / "10web_jobs_raw.csv"


def _is_armenia(job: dict) -> bool:
    loc = job.get("location", {})
    city = (loc.get("city") or "").lower()
    country = (loc.get("addressCountry") or "").lower()
    return "yerevan" in city or "armenia" in country or not loc.get("city")


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    resp = requests.get(f"{BASE}/careers/list", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    all_jobs = resp.json().get("result", [])
    armenia_jobs = [j for j in all_jobs if _is_armenia(j)]

    detail_urls = [f"{BASE}/careers/{j['id']}/detail" for j in armenia_jobs]
    job_urls = [f"https://10web.bamboohr.com/careers/{j['id']}" for j in armenia_jobs]
    new_items = [(j, u) for j, u in zip(armenia_jobs, job_urls) if u not in seen_urls]
    print(f"  [10web] {len(armenia_jobs)} Armenia, {len(new_items)} new")

    records = []
    for j, job_url in new_items:
        job_id = j["id"]
        try:
            r = requests.get(f"{BASE}/careers/{job_id}/detail", headers=HEADERS, timeout=15)
            r.raise_for_status()
            detail = r.json().get("result", r.json())
            opening = detail.get("jobOpening", detail)
            description_html = opening.get("description", "")
            full_text = html_to_text(description_html)
            loc = opening.get("location", j.get("location", {}))
            city = loc.get("city", "")
            country = loc.get("addressCountry", "Armenia")
            location = f"{city}, {country}".strip(", ") if city else "Yerevan, Armenia"
        except Exception as e:
            print(f"  [10web] ERROR detail {job_id}: {e}")
            full_text = ""
            location = "Armenia"

        records.append({
            "source": "10web",
            "source_url": job_url,
            "job_title": j.get("jobOpeningName", ""),
            "company_name": "10Web",
            "location": location,
            "department": j.get("departmentLabel", ""),
            "posting_date": "",
            "full_text": full_text,
        })
        time.sleep(0.5)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [10web] done — {count} new rows appended")
    return records
