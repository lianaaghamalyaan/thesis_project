"""Grid Dynamics scraper — Angular SPA, Playwright required."""
from __future__ import annotations

import asyncio
import re

from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE = "https://www.griddynamics.com"
LISTING_URL = f"{BASE}/careers/discover-openings"
RAW_CSV = RAW_DIR / "griddynamics_jobs_raw.csv"


def _html_to_text(h: str) -> str:
    if not h:
        return ""
    t = BeautifulSoup(str(h), "html.parser").get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


async def _scrape_async(new_urls: list[str]) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  [griddynamics] playwright not installed — skipping")
        return []

    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(LISTING_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        yerevan_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if "/careers/vacancy/" in href and ("yerevan" in text.lower() or "armenia" in text.lower()):
                full_url = BASE + href if href.startswith("/") else href
                yerevan_links.append((full_url, text))

        for url, title_hint in yerevan_links:
            if url in new_urls:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(2000)
                    detail_content = await page.content()
                    detail_soup = BeautifulSoup(detail_content, "html.parser")
                    main = detail_soup.find("main") or detail_soup.find("article")
                    full_text = _html_to_text(str(main)) if main else ""
                    h1 = detail_soup.find("h1")
                    job_title = h1.get_text(strip=True) if h1 else title_hint
                except Exception as e:
                    print(f"  [griddynamics] ERROR {url}: {e}")
                    full_text = ""
                    job_title = title_hint

                records.append({
                    "source": "griddynamics",
                    "source_url": url,
                    "job_title": job_title,
                    "company_name": "Grid Dynamics",
                    "location": "Yerevan, Armenia",
                    "posting_date": "",
                    "full_text": full_text,
                })

        await browser.close()
    return records


def _collect_live_yerevan_urls() -> list[str]:
    """Synchronously get all live Yerevan job URLs (for seen_url filtering)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(LISTING_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()
        soup = BeautifulSoup(content, "html.parser")
        urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if "/careers/vacancy/" in href and ("yerevan" in text.lower() or "armenia" in text.lower()):
                urls.append(BASE + href if href.startswith("/") else href)
        return urls
    except Exception as e:
        print(f"  [griddynamics] ERROR collecting URLs: {e}")
        return []


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    live_urls = _collect_live_yerevan_urls()
    new_urls = [u for u in live_urls if u not in seen_urls]
    print(f"  [griddynamics] {len(live_urls)} Yerevan, {len(new_urls)} new")

    if not new_urls:
        return []

    records = asyncio.run(_scrape_async(new_urls))
    count = append_new_rows(RAW_CSV, records)
    print(f"  [griddynamics] done — {count} new rows appended")
    return records
