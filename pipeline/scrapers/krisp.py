"""Krisp scraper — HTML careers page, Armenia filter."""
from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

CAREERS_URL = "https://krisp.ai/careers/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "krisp_jobs_raw.csv"


def _collect_jobs() -> list[dict]:
    resp = requests.get(CAREERS_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    listing = soup.find(id="job_listings")
    if not listing:
        return []

    jobs = []
    for a in listing.find_all("a", href=True):
        href = a["href"]
        if "/jobs/" not in href:
            continue
        url = href if href.startswith("http") else "https://krisp.ai" + href
        texts = [t.strip() for t in a.get_text("\n").split("\n") if t.strip()]
        jobs.append({
            "title": texts[0] if texts else "",
            "location": texts[1] if len(texts) > 1 else "",
            "work_type": texts[2] if len(texts) > 2 else "",
            "url": url,
        })
    return [j for j in jobs if "armenia" in j["location"].lower()]


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    armenia_jobs = _collect_jobs()
    new_jobs = [j for j in armenia_jobs if j["url"] not in seen_urls]
    print(f"  [krisp] {len(armenia_jobs)} Armenia, {len(new_jobs)} new")

    records = []
    for job in new_jobs:
        try:
            r = requests.get(job["url"], headers=HEADERS, timeout=20)
            s = BeautifulSoup(r.text, "html.parser")
            container = s.find(class_="job_data_container")
            if container:
                lines = container.get_text("\n", strip=True).split("\n")
                start = 0
                for idx, line in enumerate(lines):
                    if line.strip() in (job["location"], job["work_type"]):
                        start = idx + 1
                        break
                full_text = "\n".join(lines[start:]).strip()
            else:
                full_text = ""
        except Exception as e:
            print(f"  [krisp] ERROR {job['url']}: {e}")
            full_text = ""

        records.append({
            "source": "krisp",
            "source_url": job["url"],
            "job_title": job["title"],
            "company_name": "Krisp",
            "location": job["location"],
            "work_type": job["work_type"],
            "posting_date": "",
            "full_text": full_text,
        })
        time.sleep(DELAY_S)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [krisp] done — {count} new rows appended")
    return records
