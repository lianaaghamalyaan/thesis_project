"""NVIDIA scraper — Eightfold AI ATS, requires Playwright for session cookies."""
from __future__ import annotations

import asyncio
import re

from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE = "https://jobs.nvidia.com"
RAW_CSV = RAW_DIR / "nvidia_jobs_raw.csv"


def _html_to_text(h: str) -> str:
    if not h:
        return ""
    t = BeautifulSoup(str(h), "html.parser").get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


async def _scrape_async(seen_urls: set) -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  [nvidia] playwright not installed — skipping")
        return []

    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"{BASE}/careers", wait_until="networkidle", timeout=40000)
        await page.wait_for_timeout(2000)

        search_result = await page.evaluate("""
            async () => {
                const resp = await fetch(
                    '/api/pcsx/search?domain=nvidia.com&query=&location=Yerevan%2C+Armenia&start=0&num=100',
                    { credentials: 'include' }
                );
                return await resp.json();
            }
        """)

        positions = search_result.get("positions", []) if isinstance(search_result, dict) else []
        new_positions = [pos for pos in positions if pos.get("canonical_position_url", "") not in seen_urls]
        print(f"  [nvidia] {len(positions)} Yerevan, {len(new_positions)} new")

        for pos in new_positions:
            url = pos.get("canonical_position_url", "")
            if not url:
                continue
            try:
                detail = await page.evaluate(f"""
                    async () => {{
                        const resp = await fetch('/api/pcsx/position_details?id={pos.get("id", "")}',
                            {{ credentials: 'include' }});
                        return await resp.json();
                    }}
                """)
                desc_html = detail.get("position", {}).get("html_jobs_description", "")
                full_text = _html_to_text(desc_html)
            except Exception as e:
                print(f"  [nvidia] ERROR detail {url}: {e}")
                full_text = ""

            records.append({
                "source": "nvidia",
                "source_url": url,
                "job_title": pos.get("name", ""),
                "company_name": "NVIDIA",
                "location": "Yerevan, Armenia",
                "department": pos.get("department", ""),
                "posting_date": "",
                "full_text": full_text,
            })

        await browser.close()
    return records


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    records = asyncio.run(_scrape_async(seen_urls))
    count = append_new_rows(RAW_CSV, records)
    print(f"  [nvidia] done — {count} new rows appended")
    return records
