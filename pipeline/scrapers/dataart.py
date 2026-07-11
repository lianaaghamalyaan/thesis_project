"""DataArt scraper — React SPA, listing via window.INITIAL_STATE, detail via Playwright."""
from __future__ import annotations

import asyncio
import json
import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE_URL = "https://www.dataart.team"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY_S = 2.0
RAW_CSV = RAW_DIR / "dataart_jobs_raw.csv"


def _extract_initial_state(html: str) -> dict:
    m = re.search(r"window\.INITIAL_STATE\s*=\s*(\{.+?\})\s*;", html, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}


def _collect_yerevan_jobs() -> list[dict]:
    resp = requests.get(f"{BASE_URL}/vacancies", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    state = _extract_initial_state(resp.text)
    all_vacancies = state.get("error404", {}).get("allhotvacancies", [])
    jobs = []
    for v in all_vacancies:
        locs = [tag.get("title", "") for tag in v.get("locationTags", [])]
        if any("yerevan" in loc.lower() for loc in locs):
            slug = v.get("slug", "").lower()
            jobs.append({
                "title": v.get("title", ""),
                "slug": slug,
                "url": f"{BASE_URL}/vacancies/{slug}",
            })
    return jobs


async def _scrape_details_async(new_jobs: list[dict]) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  [dataart] playwright not installed — skipping")
        return []

    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for job in new_jobs:
            page = await browser.new_page()
            try:
                await page.goto(job["url"], wait_until="networkidle", timeout=30000)
                await page.wait_for_selector("h1", timeout=15000)
                selectors = [
                    "[class*='VacancyDetail']", "[class*='Vacancy_']",
                    "[class*='vacancy-content']", "main",
                ]
                full_text = ""
                for sel in selectors:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            full_text = await el.inner_text()
                            break
                    except Exception:
                        continue
                if not full_text:
                    full_text = await page.inner_text("body")
            except Exception as e:
                print(f"  [dataart] ERROR {job['url']}: {e}")
                full_text = ""
            finally:
                await page.close()

            records.append({
                "source": "dataart",
                "source_url": job["url"],
                "job_title": job["title"],
                "company_name": "DataArt",
                "location": "Yerevan, Armenia",
                "posting_date": "",
                "full_text": full_text.strip(),
            })
        await browser.close()
    return records


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    yerevan_jobs = _collect_yerevan_jobs()
    new_jobs = [j for j in yerevan_jobs if j["url"] not in seen_urls]
    print(f"  [dataart] {len(yerevan_jobs)} Yerevan, {len(new_jobs)} new")

    if not new_jobs:
        return []

    records = asyncio.run(_scrape_details_async(new_jobs))
    count = append_new_rows(RAW_CSV, records)
    print(f"  [dataart] done — {count} new rows appended")
    return records
