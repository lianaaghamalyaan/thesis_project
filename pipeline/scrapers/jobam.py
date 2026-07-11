"""job.am scraper — Armenian job board (category I=17 + keyword searches)."""
from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

BASE_URL = "https://job.am"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "jobam_jobs_raw.csv"

IT_TITLE_KEYWORDS = [
    "developer", "engineer", "programmer", "software", "backend", "frontend",
    "front-end", "back-end", "full stack", "fullstack", "devops", "data science",
    "data analyst", "machine learning", "ai ", "python", "java ", "javascript",
    "react", "node", ".net", "php", "qa ", "quality assurance", "tester",
    "system admin", "sysadmin", "network", "security", "cybersecurity", "cloud",
    "database", "sql", "it support", "it specialist", "1c", "web ", "mobile",
    "android", "ios", "flutter", "bitrix", "scrum", "agile",
]
IT_INDUSTRY_KEYWORD = "information te"

LISTING_SOURCES = [
    ("IT category (I=17)", f"{BASE_URL}/en/search/jobs?I=17"),
    ("keyword=developer", f"{BASE_URL}/en/jobs?q=developer"),
    ("keyword=programmer", f"{BASE_URL}/en/jobs?q=programmer"),
    ("keyword=software", f"{BASE_URL}/en/jobs?q=software"),
    ("keyword=engineer", f"{BASE_URL}/en/jobs?q=engineer"),
]

AM_HEADINGS = {
    "description": "".join(chr(c) for c in [
        0x546, 0x56f, 0x561, 0x580, 0x561, 0x563, 0x580, 0x578, 0x582, 0x569, 0x575, 0x578, 0x582, 0x576
    ]),
    "responsibilities": "".join(chr(c) for c in [
        0x54a, 0x561, 0x580, 0x57f, 0x561, 0x56f, 0x561, 0x576, 0x578, 0x582, 0x569, 0x575, 0x578,
        0x582, 0x576, 0x576, 0x565, 0x580
    ]),
    "requirements": "".join(chr(c) for c in [
        0x54a, 0x561, 0x570, 0x561, 0x576, 0x57b, 0x57e, 0x576, 0x565, 0x580
    ]),
}


def _is_it_relevant(title: str, industry: str) -> bool:
    t = title.lower()
    if IT_INDUSTRY_KEYWORD in industry.lower():
        return True
    return any(kw in t for kw in IT_TITLE_KEYWORDS)


def _get_listing_links(url: str) -> list[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [job.am] ERROR listing {url}: {e}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links = list(dict.fromkeys(
        a["href"] for a in soup.find_all("a", href=True) if "/en/job/" in a["href"]
    ))
    return [BASE_URL + l if l.startswith("/") else l for l in links]


def _scrape_detail(url: str) -> dict | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [job.am] ERROR detail {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    page = soup.find("section", class_="companyedit-page") or soup.find("div", class_="companyedit-page")
    if not page:
        return None

    title = (page.find("h1") or page.find("h2") or soup.find("h1") or soup.find("h2") or soup.new_tag("x"))
    title_text = title.get_text(strip=True)

    sections: dict[str, str] = {}
    current_key = "description"
    current_lines: list[str] = []
    en_heads = {"description", "responsibilities", "requirements", "additional notes", "skills"}

    for el in page.find_all(["h3", "p", "li", "strong"]):
        text = el.get_text(strip=True)
        if not text:
            continue
        if el.name == "h3":
            sections[current_key] = "\n".join(current_lines).strip()
            current_key = text.lower()
            current_lines = []
        elif el.name == "strong" and text.lower() in {v for v in AM_HEADINGS.values()} | en_heads:
            sections[current_key] = "\n".join(current_lines).strip()
            current_key = text.lower()
            current_lines = []
        else:
            current_lines.append(text)
    sections[current_key] = "\n".join(current_lines).strip()

    full_text = "\n\n".join(f"{k.title()}:\n{v}" for k, v in sections.items() if v).strip()
    if not full_text:
        full_text = html_to_text(str(page))

    meta_div = soup.find("div", class_="vacancy-sidebar") or soup.find("div", class_="job-details")
    company = ""
    location = ""
    employment_type = ""
    deadline = ""
    industry = ""
    posting_date = ""

    if meta_div:
        rows_text = meta_div.get_text("\n")
        for line in rows_text.split("\n"):
            l = line.strip()
            if not l:
                continue
            ll = l.lower()
            if "company" in ll:
                company = l.replace("Company", "").replace("company", "").strip(": ")
            elif "location" in ll or "city" in ll:
                location = l
            elif "employment" in ll:
                employment_type = l
            elif "deadline" in ll:
                deadline = l
            elif "industry" in ll or "categor" in ll:
                industry = l

    if not _is_it_relevant(title_text, industry):
        return None

    return {
        "source": "job.am",
        "source_url": url,
        "job_title": title_text,
        "company_name": company,
        "location": location,
        "employment_type": employment_type,
        "deadline": deadline,
        "posting_date": posting_date,
        "full_text": full_text,
    }


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    all_links: list[str] = []
    visited: set[str] = set()
    for name, url in LISTING_SOURCES:
        links = _get_listing_links(url)
        new = [l for l in links if l not in visited]
        visited.update(new)
        all_links.extend(new)
        time.sleep(DELAY_S)

    new_links = [l for l in all_links if l not in seen_urls]
    print(f"  [job.am] {len(all_links)} total, {len(new_links)} new to scrape")

    records: list[dict] = []
    for i, url in enumerate(new_links, 1):
        rec = _scrape_detail(url)
        if rec:
            records.append(rec)
        time.sleep(DELAY_S)
        if i % 20 == 0:
            print(f"  [job.am] {i}/{len(new_links)} scraped, {len(records)} kept")

    count = append_new_rows(RAW_CSV, records)
    print(f"  [job.am] done — {count} new rows appended")
    return records
