"""Synopsys scraper — HTML careers site, Yerevan location filter."""
from __future__ import annotations

import json
import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, normalize_date, load_seen_urls, append_new_rows

BASE_URL = "https://careers.synopsys.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "synopsys_jobs_raw.csv"


def _get_jsonld_job(soup: BeautifulSoup) -> dict:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "JobPosting":
                        return item
            elif data.get("@type") == "JobPosting":
                return data
        except (json.JSONDecodeError, AttributeError):
            continue
    return {}


def _collect_links() -> list[str]:
    search_url = f"{BASE_URL}/search-jobs?location=Yerevan"
    resp = requests.get(search_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/job/yerevan/" in href.lower() or "/job/armenia/" in href.lower():
            full = BASE_URL + href if href.startswith("/") else href
            if full not in seen:
                seen.add(full)
                links.append(full)
    return links


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    job_links = _collect_links()
    new_links = [l for l in job_links if l not in seen_urls]
    print(f"  [synopsys] {len(job_links)} total, {len(new_links)} new")

    records = []
    for url in new_links:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print(f"  [synopsys] ERROR {url}: {e}")
            time.sleep(DELAY_S)
            continue

        detail_soup = BeautifulSoup(r.text, "html.parser")
        jld = _get_jsonld_job(detail_soup)

        job_title = jld.get("title", "")
        location_raw = jld.get("jobLocation", "")
        if isinstance(location_raw, dict):
            addr = location_raw.get("address", {})
            location = f"{addr.get('addressLocality', '')}, {addr.get('addressCountry', 'Armenia')}".strip(", ")
        else:
            location = str(location_raw) if location_raw else "Yerevan, Armenia"

        full_text = html_to_text(jld.get("description", ""))
        employment_type = jld.get("employmentType", "")

        records.append({
            "source": "synopsys",
            "source_url": url,
            "job_title": job_title,
            "company_name": "Synopsys",
            "location": location,
            "employment_type": employment_type,
            "posting_date": normalize_date(jld.get("datePosted", "")),
            "deadline": normalize_date(jld.get("validThrough", "")),
            "full_text": full_text,
        })
        time.sleep(DELAY_S)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [synopsys] done — {count} new rows appended")
    return records
