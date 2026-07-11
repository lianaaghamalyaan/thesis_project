"""EPAM scraper — custom careers API, Armenia filter."""
from __future__ import annotations

import time

import requests

from pipeline.base import RAW_DIR, load_seen_urls, append_new_rows

SEARCH_URL = "https://careers.epam.com/api/jobs/v2/search/careers-i18n"
COUNTRY_ID = "4000741400000756803"  # Armenia
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://careers.epam.com/en/jobs",
    "Accept": "application/json",
}
RAW_CSV = RAW_DIR / "epam_jobs_raw.csv"


def _build_full_text(j: dict) -> str:
    parts = []
    if j.get("text"):
        parts.append(j["text"].strip())
    cat = j.get("category") or {}
    for key in ["responsibilities", "requirements", "nice_to_have", "technologies", "about_the_project"]:
        items = cat.get(key) or []
        if items:
            label = key.replace("_", " ").title()
            parts.append(f"{label}:\n" + "\n".join(f"- {item}" for item in items))
    return "\n\n".join(parts).strip()


def scrape(seen_urls: set | None = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = load_seen_urls(RAW_CSV)

    all_stubs: list[dict] = []
    offset = 0
    while True:
        params = {
            "facets": f"country={COUNTRY_ID}",
            "from": offset,
            "lang": "en",
            "size": 30,
            "sortBy": "relevance;relocation=asc",
        }
        try:
            data = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=20).json()
            batch = data["data"]["jobs"]
        except Exception as e:
            print(f"  [epam] ERROR offset {offset}: {e}")
            break
        if not batch:
            break
        all_stubs.extend(batch)
        total = data["data"].get("total", 0)
        if len(all_stubs) >= total:
            break
        offset += 30
        time.sleep(0.5)

    all_urls = [f"https://careers.epam.com/en/vacancy/{j.get('_key', '')}" for j in all_stubs]
    new_items = [(j, u) for j, u in zip(all_stubs, all_urls) if u not in seen_urls]
    print(f"  [epam] {len(all_stubs)} total, {len(new_items)} new")

    records = []
    for j, url in new_items:
        countries = [
            c.get("name", "") if isinstance(c, dict) else str(c)
            for c in (j.get("country") or [])
        ]
        location = ", ".join(countries) if countries else "Armenia"
        spec = j.get("job_specialization") or []
        department = ", ".join(spec) if isinstance(spec, list) else str(spec)
        primary_skill = j.get("primary_skill", "") or ""
        skills_list = [primary_skill] if primary_skill else []
        for sk in j.get("skills") or []:
            s = sk if isinstance(sk, str) else sk.get("name", "")
            if s and s not in skills_list:
                skills_list.append(s)

        records.append({
            "source": "epam",
            "source_url": url,
            "job_title": j.get("name", ""),
            "company_name": "EPAM Systems",
            "location": location,
            "seniority_level": j.get("seniority", "") or "",
            "department": department,
            "skills_tags": ", ".join(skills_list),
            "posting_date": (j.get("created_at") or "")[:10],
            "full_text": _build_full_text(j),
        })

    count = append_new_rows(RAW_CSV, records)
    print(f"  [epam] done — {count} new rows appended")
    return records
