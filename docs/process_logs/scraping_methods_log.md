# Scraping Methods Log

*Technical decisions made during data collection — for thesis methodology chapter (Chapter 3)*

---

## Overview

Job data was collected from 11 sources using a combination of techniques chosen based on each site's technical architecture. The primary principle was: **use the simplest tool that works**. Python `requests` + `BeautifulSoup` was the default; headless browser automation (`Playwright`) was used only when JavaScript execution was unavoidable.

---

## Source-by-Source Technical Decisions

### 1. LinkedIn — Apify Scraper
- **Method:** Apify cloud-based scraper (Actor: `linkedin-jobs-scraper`)
- **Why Apify:** LinkedIn aggressively blocks standard HTTP clients (bot detection, login walls, dynamic infinite scroll). Apify handles authentication, session rotation, and pagination automatically.
- **Output:** 992 postings, Armenia filter applied at collection time
- **Key fields:** `descriptionText`, `seniorityLevel`, `employmentType`, `industries`, `postedAt`
- **Limitation:** LinkedIn API is private; Apify is the standard academic/research workaround

---

### 2. Staff.am — `requests` + `BeautifulSoup` (Next.js `__NEXT_DATA__`)
- **Method:** Plain HTTP GET → parse `<script id="__NEXT_DATA__">` JSON embedded in HTML
- **Why this approach:** Staff.am is built with Next.js (server-side rendering). The full listing payload is embedded as JSON in every page's HTML source — no JavaScript execution needed. This is the most efficient pattern for SSR Next.js sites.
- **Command pattern:**
  ```python
  soup = BeautifulSoup(resp.text, "html.parser")
  next_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
  ```
- **Pagination:** `?category=1&page=N` — looped until page returned empty results
- **Detail pages:** Fetched individually; description + responsibilities + qualifications assembled into `full_text`
- **Output:** 55 non-expired jobs (4 expired jobs filtered out)

---

### 3. job.am — `requests` + `BeautifulSoup` (standard SSR HTML)
- **Method:** Plain HTTP GET → BeautifulSoup HTML parsing
- **Why:** job.am is a classic server-rendered PHP/HTML site — no JavaScript needed
- **Listing:** `GET /en/search/jobs?I=17` (IT category) + keyword searches
- **IT relevance filter:** Applied post-scrape using title keywords + industry field
- **Detail page structure:** `<section class="companyedit-page">` → `<h3>`-separated sections (Description, Responsibilities, Requirements, Additional Notes)
- **Armenian headings:** Handled via Unicode codepoint construction to avoid encoding issues:
  ```python
  AM_HEADINGS = {"requirements": "".join(chr(c) for c in [0x54a,0x561,0x570,...])}
  ```
- **Output:** 20 IT-relevant jobs (21 non-IT jobs filtered out)

---

### 4. Picsart — Greenhouse Public API
- **Method:** `GET https://boards-api.greenhouse.io/v1/boards/picsart/jobs?content=true`
- **Why:** Picsart uses Greenhouse ATS. Greenhouse exposes a fully public, unauthenticated JSON API that returns all job listings including HTML description in a single request — the cleanest possible data source.
- **Discovery:** Found Greenhouse board name (`picsart`) via JavaScript bundle inspection of the React SPA
- **Location filter:** `job["location"]["name"]` checked for "armenia" or "yerevan" (case-insensitive)
- **Command pattern:**
  ```python
  resp = requests.get("https://boards-api.greenhouse.io/v1/boards/picsart/jobs?content=true")
  jobs = resp.json()["jobs"]
  armenia_jobs = [j for j in jobs if is_armenia(j["location"]["name"])]
  ```
- **Output:** 2 Armenia jobs

---

### 5. Krisp — `requests` + `BeautifulSoup` (SSR HTML)
- **Method:** Plain HTTP GET → BeautifulSoup
- **Why:** Krisp's careers page is server-side rendered — job listings and detail pages are in the raw HTML. No JavaScript or ATS API needed.
- **Attempted first:** Lever API (`api.lever.co/v0/postings/krisp`) → 404 (Krisp does not use Lever)
- **Listing selector:** `soup.find(id="job_listings")` → all `<a href="/jobs/{slug}/">` tags
- **Card parsing:** `a.get_text("\n").split("\n")` → `[title, location, work_type]`
- **Detail selector:** `soup.find(class_="job_data_container")` → inner text
- **Armenia filter:** Applied to `location` field
- **Output:** 7 Armenia jobs

---

### 6. ServiceTitan — Workday Listing API + Playwright (detail pages)
- **Method (listing):** `POST https://servicetitan.wd1.myworkdayjobs.com/wday/cxs/servicetitan/ServiceTitan/jobs`
  - Workday exposes a public CXS (Content Experience Service) JSON API for job listings
  - Returns paginated results with job title, location, posted date, and a `bulletFields` summary
- **Method (detail):** Playwright headless Chromium
  - Why: Workday detail API (`/jobdetails`) consistently returns HTTP 500 for detail pages
  - Playwright rendered the full Workday SPA and extracted text via `[data-automation-id="job-posting-details"]`
- **Location filter:** `"Yerevan"` in job locations (from listing API response)
- **Command pattern (Playwright):**
  ```python
  async with async_playwright() as p:
      browser = await p.chromium.launch(headless=True)
      page = await browser.new_page()
      await page.goto(url, wait_until="networkidle", timeout=30000)
      await page.wait_for_selector('[data-automation-id="job-posting-details"]', timeout=10000)
      text = await page.inner_text('[data-automation-id="job-posting-details"]')
  ```
- **Output:** 4 Yerevan jobs

---

### 7. EPAM — Internal Careers Search API
- **Method:** `GET https://careers.epam.com/api/jobs/v2/search/careers-i18n`
- **Why:** EPAM's careers site is a React SPA, but it calls an internal REST API that is accessible without authentication (discovered via Playwright network interception). The API returns full job content in stub responses — no detail page scraping needed.
- **Discovery process:**
  ```python
  # Used Playwright to intercept network responses:
  page.on("response", lambda r: print(r.url) if "/api/jobs" in r.url else None)
  ```
- **Key parameters:**
  ```
  facets=country=4000741400000756803   # Armenia country code
  size=30, from=offset                  # pagination
  lang=en
  ```
- **Content structure:** `stub.text` (intro) + `stub.category.responsibilities` + `stub.category.requirements` + `stub.category.nice_to_have` → assembled into `full_text`
- **Notable parsing quirks:**
  - `seniority` is a plain string (not a list of dicts)
  - `job_specialization` is a list of strings (not list of dicts)
  - `skills` is a list of strings (not list of dicts)
- **Output:** 108 Armenia jobs

---

### 8. SoftConstruct — PeopleForce SSR HTML
- **Method:** Plain HTTP GET → BeautifulSoup
- **Why:** SoftConstruct careers are hosted on PeopleForce (`peopleforce.softconstruct.com`), which server-renders all content. No JavaScript needed.
- **Pagination:** `?page=N` loop; 196 jobs across ~20 pages (10 per page); stopped when `len(cards) < 10`
- **Card selectors:**
  ```python
  cards = soup.select("div.card-body")
  title = card.select_one("a.stretched-link").get_text(strip=True)
  meta  = card.select_one("div.tw-text-dark-neutral-80").get_text(strip=True)
  # meta format: "Department, Location"
  location = meta.rsplit(",", 1)[1].strip()
  ```
- **Armenia filter:** `"yerevan"` in location (case-insensitive)
- **Output:** 152 Yerevan jobs

---

### 9. DISQO — Lever Public API
- **Method:** `GET https://api.lever.co/v0/postings/disqo?mode=json`
- **Why:** DISQO uses Lever ATS. Like Greenhouse, Lever exposes a fully public JSON API. `mode=json` returns full job content including `descriptionPlain`, `openingPlain`, `additionalPlain`, and `lists` — no detail page scraping needed.
- **Command pattern:**
  ```python
  resp = requests.get("https://api.lever.co/v0/postings/disqo?mode=json")
  jobs = resp.json()
  armenia_jobs = [j for j in jobs if is_armenia_location(j)]
  ```
- **Location filter:** Checked `categories.location` and `workplaceType` for Armenia/Yerevan
- **Output:** 1 Armenia job

---

### 10. Synopsys — Avature SSR HTML + JSON-LD
- **Method:** Plain HTTP GET → BeautifulSoup → JSON-LD extraction
- **Why:** Synopsys careers uses Avature ATS. The site is server-side rendered. Each detail page contains a `<script type="application/ld+json">` block with `@type: JobPosting` including the full `description` HTML.
- **Location filter:** Used URL parameter `?location=Yerevan` on the listing page
- **Listing selector:**
  ```python
  links = [a["href"] for a in soup.find_all("a", href=True)
           if "/job/yerevan/" in a["href"].lower()]
  ```
- **Detail content:**
  ```python
  jld = next(json.loads(s.string) for s in soup.find_all("script", type="application/ld+json")
             if "JobPosting" in (s.string or ""))
  full_text = html_to_text(jld["description"])
  ```
- **Output:** 2 Yerevan jobs (both internships)

---

### 11. DataArt — Custom React SPA (INITIAL_STATE + Playwright)
- **Method (listing):** `requests` → parse `window.INITIAL_STATE` JSON embedded in raw HTML
- **Method (detail):** Playwright headless Chromium
- **Why hybrid:** The listing page embeds all job metadata in `window.INITIAL_STATE` (a server-injected JSON blob) — parseable without JavaScript. But the actual job descriptions (requirements, responsibilities, tech stack) are loaded and rendered client-side by React — Playwright is required.
- **Listing parsing:**
  ```python
  m = re.search(r"window\.INITIAL_STATE\s*=\s*(\{.+?\})\s*;", html, re.DOTALL)
  state = json.loads(m.group(1))
  vacancies = state["error404"]["allhotvacancies"]
  yerevan = [v for v in vacancies
             if any("yerevan" in t["title"].lower() for t in v["locationTags"])]
  ```
- **Metadata from detail page INITIAL_STATE:** `microData[N]["@type" == "JobPosting"]` → `datePosted`, `employmentType`, `industry`
- **Full content:** Playwright → `wait_for_selector("h1")` → extract vacancy content container
- **Output:** 5 Yerevan jobs

---

## General Patterns and Reusable Code

### `html_to_text()` — HTML stripping
Used across all scrapers that receive HTML content (Greenhouse, Synopsys JSON-LD, etc.):
```python
def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["p", "li", "br", "h1", "h2", "h3", "h4"]):
        tag.insert_before("\n")
    text = soup.get_text(" ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
```

### `normalize_date()` — Date standardization
All dates normalized to `YYYY-MM-DD`:
```python
def normalize_date(val):
    # ISO with varying zero-padding: "2026-3-9" → "2026-03-09"
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", str(val))
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # M/D/YYYY format (job.am, Staff.am)
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", str(val))
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return str(val)
```

### Playwright async pattern
Used for ServiceTitan (Workday) and DataArt (custom React SPA):
```python
async def scrape_detail(browser, url):
    page = await browser.new_page()
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_selector("h1", timeout=10000)
    text = await page.inner_text("main")
    await page.close()
    return text

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for url in urls:
            text = await scrape_detail(browser, url)
        await browser.close()

asyncio.run(run())
```

### Rate limiting
All scrapers use `time.sleep(1.5)` or `asyncio.sleep(2.0)` between requests. Headers always include:
```python
"User-Agent": "Mozilla/5.0 (compatible; ThesisResearch/1.0; Armenian IT curriculum alignment; academic use)"
```

---

## ATS / Platform Summary

| Source | Platform | Technique |
|---|---|---|
| LinkedIn | LinkedIn (proprietary) | Apify cloud scraper |
| Staff.am | Custom Next.js | `__NEXT_DATA__` JSON parsing |
| job.am | Custom PHP/HTML | BeautifulSoup HTML parsing |
| Picsart | Greenhouse ATS | Public JSON API |
| Krisp | Custom SSR | BeautifulSoup HTML parsing |
| ServiceTitan | Workday | CXS API (listing) + Playwright (detail) |
| EPAM | Custom React | Internal API (network interception) |
| SoftConstruct | PeopleForce | BeautifulSoup HTML parsing |
| DISQO | Lever ATS | Public JSON API |
| Synopsys | Avature ATS | SSR HTML + JSON-LD |
| DataArt | Custom React | `window.INITIAL_STATE` + Playwright |

---

## robots.txt Compliance

All sites were checked for robots.txt restrictions before scraping. No site explicitly disallowed scraping of their public job listing pages. Sites that disallow specific paths (job.am: `/API/*`, `/search/topjobs`; LinkedIn: most paths) were respected by using only allowed endpoints or third-party tools (Apify).
