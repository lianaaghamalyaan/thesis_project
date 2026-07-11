"""SoftConstruct scraper — PeopleForce careers portal, Armenia filter."""
from __future__ import annotations

import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE = "https://peopleforce.softconstruct.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
}
DELAY_LISTING = 0.5
DELAY_DETAIL = 1.0
RAW_CSV = RAW_DIR / "softconstruct_jobs_raw.csv"

BOILERPLATE = {
    "SOFTCONSTRUCT", "Open Positions", "Home", "Apply now", "Share", "Link",
    "Share to", "Powered by", "PeopleForce", "English", "Українська", "Polski",
    "Español", "Português", "Deutsch", "Русский",
}


def _clean_detail_text(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(["nav", "footer", "header"]):
        tag.decompose()
    for tag in soup.find_all(True, class_=lambda c: c and any(
            kw in " ".join(c).lower() for kw in ["nav", "footer", "header", "share", "powered"])):
        tag.decompose()
    body = soup.find("body")
    raw = body.get_text("\n", strip=True) if body else ""
    lines = [
        l for l in raw.split("\n")
        if l.strip() and l.strip() not in BOILERPLATE
        and not l.strip().startswith("SOFTCONSTRUCT -")
    ]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _collect_cards() -> list[dict]:
    all_cards = []
    page = 1
    while True:
        url = f"{BASE}/careers?page={page}"
        try:
            soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
        except Exception:
            break
        cards = soup.find_all("div", class_="card-body")
        if not cards:
            break
        for card in cards:
            a = card.find("a", class_="stretched-link")
            meta = card.find("div", class_="tw-text-dark-neutral-80")
            if not a:
                continue
            href = a["href"]
            title = a.get_text(strip=True)
            meta_text = meta.get_text(strip=True) if meta else ""
            dept = meta_text.rsplit(",", 1)[0].strip() if "," in meta_text else meta_text
            loc = meta_text.rsplit(",", 1)[1].strip() if "," in meta_text else ""
            all_cards.append({
                "url": BASE + href if href.startswith("/") else href,
                "title": title,
                "department": dept,
                "location": loc,
            })
        if len(cards) < 10:
            break
        page += 1
        time.sleep(DELAY_LISTING)
    return all_cards


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    all_cards = _collect_cards()
    armenia = [
        c for c in all_cards
        if "yerevan" in c["location"].lower() or "armenia" in c["location"].lower()
    ]
    new_cards = [c for c in armenia if c["url"] not in seen_urls]
    print(f"  [softconstruct] {len(armenia)} Armenia, {len(new_cards)} new")

    records = []
    for c in new_cards:
        try:
            r = requests.get(c["url"], headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            full_text = _clean_detail_text(soup)
        except Exception as e:
            print(f"  [softconstruct] ERROR {c['url']}: {e}")
            full_text = ""

        records.append({
            "source": "softconstruct",
            "source_url": c["url"],
            "job_title": c["title"],
            "company_name": "SoftConstruct",
            "location": c["location"],
            "department": c["department"],
            "posting_date": "",
            "full_text": full_text,
        })
        time.sleep(DELAY_DETAIL)

    count = append_new_rows(RAW_CSV, records)
    print(f"  [softconstruct] done — {count} new rows appended")
    return records
