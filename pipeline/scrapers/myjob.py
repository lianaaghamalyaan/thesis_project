"""myjob.am scraper — Armenian job board (ASP.NET, pagination via Default.aspx?pg=N)."""
from __future__ import annotations

import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

BASE_URL = "https://www.myjob.am"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL + "/",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "myjob_jobs_raw.csv"

IT_TITLE_KEYWORDS = [
    "developer", "engineer", "programmer", "software", "backend", "frontend",
    "devops", "data scientist", "data analyst", "machine learning", "python",
    "java", "javascript", "react", "node", ".net", "php", "qa ", "tester",
    "security", "cloud", "sql", "mobile", "android", "ios", "it support",
    "it specialist", "web developer", "system administrator", "sysadmin",
]
IT_CATEGORIES = ["information", "it ", "software", "technology", "computer"]


def _is_it_relevant(title: str, category: str) -> bool:
    t = title.lower()
    if any(k in category.lower() for k in IT_CATEGORIES):
        return True
    return any(kw in t for kw in IT_TITLE_KEYWORDS)


def _collect_job_ids() -> list[str]:
    """Page through Default.aspx and collect all jobId values."""
    ids: list[str] = []
    seen: set[str] = set()
    page = 1
    while True:
        url = f"{BASE_URL}/Default.aspx" + (f"?pg={page}" if page > 1 else "")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [myjob.am] ERROR page {page}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        links = [
            a["href"] for a in soup.find_all("a", href=True)
            if "Announcement.aspx" in a["href"]
        ]
        if not links:
            break

        new_found = False
        for href in links:
            m = re.search(r"jobId=(\d+)", href)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                ids.append(m.group(1))
                new_found = True

        if not new_found:
            break

        pg_links = [a["href"] for a in soup.find_all("a", href=True) if "pg=" in a["href"]]
        max_page = max(
            (int(re.search(r"pg=(\d+)", l).group(1)) for l in pg_links if re.search(r"pg=(\d+)", l)),
            default=page,
        )
        if page >= max_page:
            break
        page += 1
        time.sleep(DELAY_S)

    return ids


def _scrape_detail(job_id: str) -> dict | None:
    url = f"{BASE_URL}/Announcement.aspx?jobId={job_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [myjob.am] ERROR detail {job_id}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    title_el = soup.find(class_="fullJobPosition")
    title = title_el.get_text(strip=True) if title_el else ""

    company_els = soup.find_all(class_="fullJobTextLong")
    company = company_els[0].get_text(strip=True) if company_els else ""

    short_texts = soup.find(class_="fullJobTextsShort")
    short_parts = short_texts.get_text(strip=True).split("\n") if short_texts else []
    category = short_parts[0] if len(short_parts) > 0 else ""
    deadline = short_parts[-1] if len(short_parts) >= 3 else ""

    location_el = soup.find(class_="fullJobTextShortMiddle")
    location = location_el.get_text(strip=True) if location_el else ""

    # Full text from all section bodies (skip first which is company)
    sections = soup.find_all(class_="fullJobTextLong")
    section_titles = soup.find_all(class_="fullJobTitleLong")
    parts = []
    for header, body in zip(section_titles[1:], sections[1:]):
        h = header.get_text(strip=True)
        b = body.get_text("\n", strip=True)
        if h and b and h.lower() not in ("application procedures",):
            parts.append(f"{h}:\n{b}")
    full_text = "\n\n".join(parts).strip()

    if not _is_it_relevant(title, category):
        return None

    return {
        "source": "myjob.am",
        "source_url": url,
        "job_title": title,
        "company_name": company,
        "location": location,
        "category": category,
        "deadline": deadline,
        "posting_date": "",
        "full_text": full_text,
    }


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    all_ids = _collect_job_ids()
    new_ids = [
        jid for jid in all_ids
        if f"{BASE_URL}/Announcement.aspx?jobId={jid}" not in seen_urls
    ]
    print(f"  [myjob.am] {len(all_ids)} total, {len(new_ids)} new to scrape")

    records: list[dict] = []
    for i, jid in enumerate(new_ids, 1):
        rec = _scrape_detail(jid)
        if rec:
            records.append(rec)
        time.sleep(DELAY_S)
        if i % 20 == 0:
            print(f"  [myjob.am] {i}/{len(new_ids)} scraped, {len(records)} IT jobs kept")

    count = append_new_rows(RAW_CSV, records)
    print(f"  [myjob.am] done — {count} new rows appended")
    return records
