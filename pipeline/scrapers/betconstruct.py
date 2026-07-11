"""BetConstruct scraper — Workable ATS public board."""
from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

BOARD_URL = "https://apply.workable.com/betconstruct/"
API_URL = "https://apply.workable.com/api/v3/accounts/betconstruct/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept": "application/json",
    "Referer": BOARD_URL,
}
DELAY_S = 1.0
RAW_CSV = RAW_DIR / "betconstruct_jobs_raw.csv"


def _is_armenia(job: dict) -> bool:
    loc = job.get("location", {})
    city = (loc.get("city") or loc.get("location") or "").lower()
    country = (loc.get("country") or "").lower()
    return "armenia" in country or "yerevan" in city or "am" == country


def _collect_jobs() -> list[dict]:
    all_jobs = []
    payload = {"query": "", "location": [], "department": [], "worktype": [], "remote": []}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        resp.raise_for_status()
        all_jobs = resp.json().get("results", [])
    except Exception:
        try:
            resp = requests.get(f"{API_URL}?limit=100", headers=HEADERS, timeout=20)
            resp.raise_for_status()
            all_jobs = resp.json().get("results", [])
        except Exception as e:
            print(f"  [betconstruct] ERROR collecting jobs: {e}")
    return [j for j in all_jobs if _is_armenia(j)]


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    armenia_jobs = _collect_jobs()
    job_urls = [f"https://apply.workable.com/betconstruct/j/{j.get('shortcode', '')}" for j in armenia_jobs]
    new_items = [(j, u) for j, u in zip(armenia_jobs, job_urls) if u not in seen_urls]
    print(f"  [betconstruct] {len(armenia_jobs)} Armenia, {len(new_items)} new")

    records = []
    for job, url in new_items:
        try:
            r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            desc_el = soup.find("div", attrs={"data-ui": "job-description"}) or \
                      soup.find("div", class_=lambda c: c and "description" in str(c).lower())
            full_text = desc_el.get_text("\n", strip=True) if desc_el else html_to_text(r.text[:10000])
        except Exception as e:
            print(f"  [betconstruct] ERROR detail {url}: {e}")
            full_text = ""

        loc = job.get("location", {})
        location = f"{loc.get('city', 'Yerevan')}, {loc.get('country', 'Armenia')}".strip(", ")

        records.append({
            "source": "betconstruct",
            "source_url": url,
            "job_title": job.get("title", ""),
            "company_name": "BetConstruct",
            "location": location,
            "department": job.get("department", ""),
            "employment_type": job.get("employment_type", ""),
            "posting_date": (job.get("published_on") or "")[:10],
            "full_text": full_text,
        })
        time.sleep(DELAY_S)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [betconstruct] done — {count} new rows appended")
    return records
