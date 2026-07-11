"""staff.am scraper — Next.js SSR job board (Software Development category)."""
from __future__ import annotations

import json
import re
import time

import requests
from bs4 import BeautifulSoup

from pipeline.base import RAW_DIR, html_to_text, load_seen_urls, append_new_rows

BASE_URL = "https://staff.am"
CATEGORY = 1  # Software Development
HEADERS = {"User-Agent": "ThesisResearch/1.0 (Armenian IT curriculum alignment; academic use)"}
DELAY_S = 1.5
RAW_CSV = RAW_DIR / "staffam_jobs_raw.csv"


def _get_en(field) -> str:
    if isinstance(field, dict):
        return field.get("en") or field.get("am") or field.get("ru") or ""
    return str(field) if field else ""


def _get_skills_list(skills_raw) -> list[str]:
    if not skills_raw or not isinstance(skills_raw, list):
        return []
    return [_get_en(s.get("title", "")).strip() for s in skills_raw if s.get("title")]


def _card_to_detail_url(card) -> str:
    slug_val = card.get("slug", {})
    slug = (
        slug_val.get("en") or slug_val.get("am") or slug_val.get("ru") or ""
        if isinstance(slug_val, dict) else str(slug_val).strip()
    )
    cat = card.get("category", {})
    cat_code = cat.get("code", "jobs") if isinstance(cat, dict) else "jobs"
    return f"{BASE_URL}/en/jobs/{cat_code}/{slug}" if slug else ""


def _card_posting_date(card) -> str:
    for field in ("published_at", "created_at", "updated_at"):
        val = card.get(field, "")
        if val:
            return str(val)[:10]
    return ""


def _scrape_detail(url: str) -> dict | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [staff.am] ERROR {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    nd_tag = soup.find("script", id="__NEXT_DATA__")
    if not nd_tag:
        return None

    try:
        data = json.loads(nd_tag.string)
        job = data["props"]["pageProps"]["job"]
    except (KeyError, json.JSONDecodeError, TypeError):
        return None

    companies = job.get("companiesStruct", [])
    company = _get_en(companies[0].get("title", {})) if companies else ""

    city = job.get("job_city", {})
    location_city = _get_en(city.get("title", {})) if isinstance(city, dict) else ""
    is_remote = job.get("is_remote", False)
    location = location_city or ("Remote" if is_remote else "Armenia")

    emp_type_raw = job.get("employment_type", {})
    employment_type = _get_en(emp_type_raw) if isinstance(emp_type_raw, dict) else str(emp_type_raw or "")

    cand_level = job.get("job_candidate_level", {})
    seniority = _get_en(cand_level.get("title", {})) if isinstance(cand_level, dict) else ""

    skills_tags = ", ".join(_get_skills_list(job.get("skills", [])))
    deadline = str(job.get("deadline", "") or "")[:10]

    desc_html = job.get("description", "") or ""
    resp_html = job.get("responsibilities", "") or ""
    req_html = job.get("required_qualifications", "") or ""
    full_text = "\n\n".join(filter(None, [
        html_to_text(desc_html),
        html_to_text(resp_html),
        html_to_text(req_html),
    ]))

    return {
        "source": "staff.am",
        "source_url": url,
        "job_title": _get_en(job.get("title", {})),
        "company_name": company,
        "location": location,
        "employment_type": employment_type,
        "seniority_level": seniority,
        "skills_tags": skills_tags,
        "deadline": deadline,
        "posting_date": str(job.get("published_at", "") or "")[:10],
        "full_text": full_text,
    }


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    all_cards: list[dict] = []
    page = 1
    while True:
        url = f"{BASE_URL}/en/jobs?category={CATEGORY}&page={page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  [staff.am] ERROR page {page}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        nd_tag = soup.find("script", id="__NEXT_DATA__")
        if not nd_tag:
            break

        data = json.loads(nd_tag.string)
        try:
            jobs_raw = data["props"]["pageProps"]["jobs"]
            jobs_on_page = jobs_raw if isinstance(jobs_raw, list) else jobs_raw.get("data", [])
        except (KeyError, TypeError):
            jobs_on_page = []

        if not jobs_on_page:
            break

        all_cards.extend(jobs_on_page)
        page += 1
        time.sleep(DELAY_S)

    detail_urls = [(c, _card_to_detail_url(c), _card_posting_date(c)) for c in all_cards]
    detail_urls = [(c, u, d) for c, u, d in detail_urls if u]

    new_items = [(c, u, d) for c, u, d in detail_urls if u not in seen_urls]
    print(f"  [staff.am] {len(detail_urls)} total, {len(new_items)} new to scrape")

    records: list[dict] = []
    for i, (card, url, _) in enumerate(new_items, 1):
        rec = _scrape_detail(url)
        if rec:
            records.append(rec)
        time.sleep(DELAY_S)
        if i % 20 == 0:
            print(f"  [staff.am] {i}/{len(new_items)} scraped")

    count = append_new_rows(RAW_CSV, records)
    print(f"  [staff.am] done — {count} new rows appended")
    return records
