"""ServiceTitan scraper — Workday ATS, Playwright for detail pages."""
from __future__ import annotations

import asyncio
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

BASE_WD = "https://servicetitan.wd1.myworkdayjobs.com"
LIST_URL = f"{BASE_WD}/wday/cxs/servicetitan/ServiceTitan/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; academic use)",
    "Content-Type": "application/json",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "servicetitan_jobs_raw.csv"


def _collect_armenia_jobs() -> list[dict]:
    all_jobs = []
    offset = 0
    while True:
        try:
            data = requests.post(
                LIST_URL, headers=HEADERS,
                json={"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""},
                timeout=20,
            ).json()
            batch = data.get("jobPostings", [])
        except Exception as e:
            print(f"  [servicetitan] ERROR listing offset {offset}: {e}")
            break
        if not batch:
            break
        all_jobs.extend(batch)
        if len(all_jobs) >= data.get("total", 0):
            break
        offset += 20
        time.sleep(0.5)

    return [
        j for j in all_jobs
        if "armenia" in j.get("locationsText", "").lower()
        or "yerevan" in j.get("locationsText", "").lower()
    ]


async def _scrape_details_async(jobs: list[dict]) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  [servicetitan] playwright not installed — skipping detail scrape")
        return []

    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for job in jobs:
            url = f"{BASE_WD}/ServiceTitan{job['externalPath']}"
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                try:
                    await page.wait_for_selector('[data-automation-id="job-posting-details"]', timeout=10000)
                except Exception:
                    await page.wait_for_timeout(3000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                detail_div = soup.find(attrs={"data-automation-id": "job-posting-details"})
                full_text = detail_div.get_text("\n", strip=True) if detail_div else html_to_text(content)
            except Exception as e:
                print(f"  [servicetitan] ERROR {url}: {e}")
                full_text = ""
                url = f"{BASE_WD}/ServiceTitan{job['externalPath']}"

            records.append({
                "source": "servicetitan",
                "source_url": url,
                "job_title": job.get("title", ""),
                "company_name": "ServiceTitan",
                "location": job.get("locationsText", ""),
                "posting_date": "",
                "full_text": full_text,
            })
        await browser.close()
    return records


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    armenia_jobs = _collect_armenia_jobs()
    new_jobs = [
        j for j in armenia_jobs
        if f"{BASE_WD}/ServiceTitan{j.get('externalPath', '')}" not in seen_urls
    ]
    print(f"  [servicetitan] {len(armenia_jobs)} Armenia, {len(new_jobs)} new")

    if not new_jobs:
        return []

    records = asyncio.run(_scrape_details_async(new_jobs))
    count = append_new_rows(RAW_CSV, records)
    print(f"  [servicetitan] done — {count} new rows appended")
    return records
