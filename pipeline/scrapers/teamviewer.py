"""TeamViewer scraper — TeamTailor ATS, Armenia/Yerevan filter."""
from __future__ import annotations

import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE_URL = "https://careers.teamviewer.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "teamviewer_jobs_raw.csv"


def _collect_armenia_jobs() -> list[dict]:
    jobs = []
    seen = set()
    page = 1
    while True:
        url = f"{BASE_URL}/jobs" + (f"?page={page}" if page > 1 else "")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [teamviewer] ERROR page {page}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        job_links = [
            a for a in soup.find_all("a", href=True)
            if re.search(r"/jobs/\d+-", a["href"])
        ]
        if not job_links:
            break

        new_found = False
        for a in job_links:
            href = a["href"]
            full_url = BASE_URL + href if href.startswith("/") else href
            text = a.get_text(strip=True).lower()
            if full_url in seen:
                continue
            seen.add(full_url)
            if "yerevan" in text or "armenia" in text:
                title = a.get_text(strip=True)
                jobs.append({"url": full_url, "title": title})
                new_found = True

        show_more = soup.find("a", href=lambda h: h and "show_more" in str(h))
        if not show_more and not new_found:
            break
        page += 1
        time.sleep(DELAY_S)

    return jobs


def _scrape_detail(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        content = (
            soup.find("div", class_=lambda c: c and "description" in str(c).lower()) or
            soup.find("article") or
            soup.find("main")
        )
        return content.get_text("\n", strip=True) if content else ""
    except Exception as e:
        print(f"  [teamviewer] ERROR {url}: {e}")
        return ""


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    armenia_jobs = _collect_armenia_jobs()
    new_jobs = [j for j in armenia_jobs if j["url"] not in seen_urls]
    print(f"  [teamviewer] {len(armenia_jobs)} Armenia, {len(new_jobs)} new")

    records = []
    for job in new_jobs:
        full_text = _scrape_detail(job["url"])
        records.append({
            "source": "teamviewer",
            "source_url": job["url"],
            "job_title": job["title"],
            "company_name": "TeamViewer",
            "location": "Yerevan, Armenia",
            "posting_date": "",
            "full_text": full_text,
        })
        time.sleep(DELAY_S)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [teamviewer] done — {count} new rows appended")
    return records
