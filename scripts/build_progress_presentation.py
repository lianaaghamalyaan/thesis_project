from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


W, H = 1376, 768
M = 58

BG = "#f7f4ee"
NAVY = "#203a63"
BLUE = "#4d76b2"
SOFT_BLUE = "#dfe9f7"
TEAL = "#73b7ae"
SOFT_TEAL = "#dff2ef"
AMBER = "#d8a44c"
SOFT_AMBER = "#f6ead5"
ROSE = "#e7d7d2"
DARK = "#202733"
GRAY = "#5f6773"
MUTED = "#7a828d"
WHITE = "#ffffff"
LINE = "#c9d1db"
SHADOW = "#d8d2c8"

OUT_DIR = Path("docs/presentation/generated")
SLIDES_DIR = OUT_DIR / "thesis_progress_slides"
PDF_PATH = OUT_DIR / "thesis_progress_deck.pdf"


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = load_font(42, True)
F_SUB = load_font(20)
F_SECTION = load_font(24, True)
F_STEP = load_font(18, True)
F_BODY = load_font(17)
F_SMALL = load_font(14)
F_TINY = load_font(12)
F_NUM = load_font(34, True)
F_BIG = load_font(60, True)


def new_slide(title: str, subtitle: str = ""):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.line((48, 34, W - 48, 34), fill=SOFT_BLUE, width=6)
    draw.text((M, 58), title, fill=DARK, font=F_TITLE)
    if subtitle:
        draw.text((M, 112), subtitle, fill=GRAY, font=F_SUB)
    return img, draw


def footer(draw: ImageDraw.ImageDraw, n: int):
    draw.text((M, H - 28), f"Master's thesis progress presentation | Slide {n}", fill=MUTED, font=F_TINY)
    draw.text((W - 340, H - 28), "Armenian IT Curriculum - Labor Market Alignment", fill=MUTED, font=F_TINY)


def rounded_box(draw, box, fill=WHITE, outline=LINE, radius=24, shadow=True):
    x1, y1, x2, y2 = box
    if shadow:
        draw.rounded_rectangle((x1 + 6, y1 + 8, x2 + 6, y2 + 8), radius=radius, fill=SHADOW)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def wrapped(draw, text, font, width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if draw.textlength(test, font=font) <= width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_bullets(draw, x, y, items, width, line_gap=8):
    cy = y
    for item in items:
        lines = wrapped(draw, item, F_BODY, width - 24)
        draw.ellipse((x, cy + 7, x + 8, cy + 15), fill=BLUE)
        draw.text((x + 18, cy), lines[0], fill=DARK, font=F_BODY)
        cy += 24
        for line in lines[1:]:
            draw.text((x + 18, cy), line, fill=GRAY, font=F_BODY)
            cy += 22
        cy += line_gap
    return cy


def metric_card(draw, x, y, w, h, number, title, desc, tint, accent):
    rounded_box(draw, (x, y, x + w, y + h))
    draw.rounded_rectangle((x + 16, y + 18, x + 120, y + 84), radius=18, fill=tint)
    draw.text((x + 34, y + 29), str(number), fill=accent, font=F_NUM)
    draw.text((x + 138, y + 22), title, fill=DARK, font=F_STEP)
    draw.text((x + 138, y + 56), desc, fill=GRAY, font=F_SMALL)


def chip(draw, x, y, text, fill=WHITE, outline=LINE, accent=DARK):
    pad_x = 14
    w = int(draw.textlength(text, font=F_SMALL)) + pad_x * 2
    h = 34
    draw.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=fill, outline=outline, width=2)
    draw.text((x + pad_x, y + 8), text, fill=accent, font=F_SMALL)
    return w


def hbars(draw, x, y, labels, values, max_value, width, color):
    cy = y
    for label, value in zip(labels, values):
        draw.text((x, cy), label, fill=DARK, font=F_SMALL)
        bx = x + 170
        by = cy + 4
        bw = int((value / max_value) * width)
        draw.rounded_rectangle((bx, by, bx + width, by + 18), radius=9, fill="#ebedf1")
        draw.rounded_rectangle((bx, by, bx + bw, by + 18), radius=9, fill=color)
        draw.text((bx + width + 10, cy), f"{value}", fill=GRAY, font=F_SMALL)
        cy += 34


def table(draw, x, y, col_widths, headers, rows, row_h=36):
    total_w = sum(col_widths)
    draw.rounded_rectangle((x, y, x + total_w, y + row_h), radius=12, fill=SOFT_BLUE, outline=LINE, width=2)
    cx = x
    for w, head in zip(col_widths, headers):
        draw.text((cx + 12, y + 9), head, fill=NAVY, font=F_SMALL)
        cx += w
    cy = y + row_h
    for row in rows:
        draw.rounded_rectangle((x, cy, x + total_w, cy + row_h), radius=0, fill=WHITE, outline=LINE, width=1)
        cx = x
        for w, cell in zip(col_widths, row):
            draw.text((cx + 12, cy + 9), str(cell), fill=DARK, font=F_SMALL)
            cx += w
        cy += row_h


def process_boxes(draw, x, y, steps, box_w=170, box_h=118, gap=18):
    fills = [SOFT_BLUE, SOFT_TEAL, SOFT_AMBER, SOFT_BLUE, SOFT_TEAL, SOFT_AMBER, SOFT_BLUE]
    accents = [NAVY, "#2c6b64", "#8d6220", NAVY, "#2c6b64", "#8d6220", NAVY]
    for i, (num, title, desc) in enumerate(steps):
        bx = x + i * (box_w + gap)
        rounded_box(draw, (bx, y, bx + box_w, y + box_h), radius=22)
        draw.rounded_rectangle((bx + 14, y + 14, bx + 48, y + 48), radius=12, fill=fills[i])
        draw.text((bx + 26, y + 20), num, fill=accents[i], font=F_STEP)
        draw.text((bx + 58, y + 18), title, fill=DARK, font=F_STEP)
        lines = wrapped(draw, desc, F_SMALL, box_w - 24)
        cy = y + 58
        for line in lines[:3]:
            draw.text((bx + 14, cy), line, fill=GRAY, font=F_SMALL)
            cy += 20
        if i < len(steps) - 1:
            ax1 = bx + box_w + 4
            ay = y + 58
            ax2 = bx + box_w + gap - 5
            draw.line((ax1, ay, ax2, ay), fill=BLUE, width=5)
            draw.polygon([(ax2, ay), (ax2 - 12, ay - 8), (ax2 - 12, ay + 8)], fill=BLUE)


def save_slides(slides):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, slide in enumerate(slides, start=1):
        path = SLIDES_DIR / f"slide_{i:02d}.png"
        slide.save(path)
        paths.append(path)
    rgb_slides = [s.convert("RGB") for s in slides]
    rgb_slides[0].save(PDF_PATH, save_all=True, append_images=rgb_slides[1:], resolution=150.0)
    return paths


def slide_01():
    img, d = new_slide("Armenian IT Curriculum vs. Labor Market Alignment", "Master's thesis progress presentation")
    rounded_box(d, (70, 170, 570, 520), fill=WHITE)
    d.text((110, 210), "Research Question", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        110,
        258,
        [
            "How well do IT curricula from selected Armenian universities align with current Armenian IT job market demands?",
            "Goal: build a reproducible, data-driven pipeline instead of relying only on qualitative discussion.",
            "Current stage: analytical pipeline complete, thesis writing and coverage improvement in progress.",
        ],
        400,
    )
    rounded_box(d, (640, 170, 1290, 520), fill=WHITE)
    d.text((678, 214), "Why This Matters", fill=NAVY, font=F_SECTION)
    metric_card(d, 690, 260, 260, 92, "4", "Universities", "current curriculum dataset", SOFT_BLUE, NAVY)
    metric_card(d, 980, 260, 260, 92, "753", "IT-only jobs", "analysis subset after filtering", SOFT_TEAL, "#2c6b64")
    d.text((702, 390), "Practical value", fill=DARK, font=F_STEP)
    draw_bullets(
        d,
        702,
        424,
        [
            "Shows where curricula already match market demand.",
            "Identifies gaps in applied competences and modern tools.",
            "Can later be reused for repeated alignment checks.",
        ],
        520,
    )
    footer(d, 1)
    return img


def slide_02():
    img, d = new_slide("Project Scope and Current Dataset", "Education corpus and labor-market corpus used in the current analysis")
    metric_card(d, 64, 168, 385, 102, "1,161", "Curriculum Data", "courses from 4 universities / 25 programs", SOFT_BLUE, NAVY)
    metric_card(d, 495, 168, 385, 102, "1,369", "Broad Job Snapshot", "postings from 14 sources", SOFT_TEAL, "#2c6b64")
    metric_card(d, 926, 168, 385, 102, "753", "IT-Only Set", "postings kept for downstream NLP", SOFT_AMBER, "#8d6220")
    table(
        d,
        64,
        324,
        [360, 120, 120, 300],
        ["University", "Programs", "Courses", "Description availability"],
        [
            ["YSU", "13", "691", "Translated Armenian descriptions"],
            ["AUA", "7", "249", "English descriptions"],
            ["NUACA", "4", "174", "Mostly names only"],
            ["RAU", "1", "47", "Mostly names only"],
        ],
    )
    rounded_box(d, (880, 324, 1290, 620))
    d.text((908, 354), "Important Scope Note", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        908,
        406,
        [
            "This is not yet the full Armenian higher-education landscape.",
            "NPUA and UFAR are still missing from the dataset.",
            "RAU is only partially covered at this stage.",
        ],
        340,
    )
    footer(d, 2)
    return img


def slide_03():
    img, d = new_slide("How University Data Was Collected", "Different universities required different collection methods because their data formats were very different")
    boxes = [
        ("YSU", "Apify + rendered markdown pages", "691 courses | Armenian | rich text after translation"),
        ("AUA", "direct HTML course catalog parsing", "249 courses | English | strongest description coverage"),
        ("NUACA", "web scraping of plain-text course lists", "174 courses | English names only"),
        ("RAU", "PDF parsing with PyPDF2 + regex", "47 courses | Russian -> English titles"),
    ]
    positions = [(64, 180), (720, 180), (64, 392), (720, 392)]
    fills = [SOFT_BLUE, SOFT_TEAL, SOFT_AMBER, ROSE]
    for (title, method, desc), (x, y), fill in zip(boxes, positions, fills):
        rounded_box(d, (x, y, x + 592, y + 150), fill=WHITE)
        d.rounded_rectangle((x + 18, y + 20, x + 110, y + 68), radius=18, fill=fill)
        d.text((x + 40, y + 30), title, fill=DARK, font=F_STEP)
        d.text((x + 132, y + 26), method, fill=NAVY, font=F_STEP)
        for i, line in enumerate(wrapped(d, desc, F_BODY, 430)):
            d.text((x + 132, y + 62 + i * 24), line, fill=GRAY, font=F_BODY)
    d.text((64, 660), "Key takeaway: the curriculum corpus was built from heterogeneous web pages and PDFs, then merged into one unified dataset.", fill=GRAY, font=F_BODY)
    footer(d, 3)
    return img


def slide_04():
    img, d = new_slide("How Job Data Was Collected", "The job corpus combines broad aggregators with direct employer portals")
    rounded_box(d, (64, 170, 580, 614))
    d.text((92, 204), "Main public sources", fill=NAVY, font=F_SECTION)
    x, y = 92, 258
    for name, fill in [("LinkedIn", SOFT_BLUE), ("Staff.am", SOFT_TEAL), ("job.am", SOFT_AMBER)]:
        w = chip(d, x, y, name, fill=fill, accent=DARK)
        x += w + 14
    y = 320
    d.text((92, y), "Company portals used in the current snapshot", fill=DARK, font=F_STEP)
    x, y = 92, 360
    row_items = ["EPAM", "SoftConstruct", "Grid Dynamics", "Krisp", "NVIDIA", "10Web", "DataArt", "ServiceTitan", "Synopsys", "Picsart", "DISQO"]
    for item in row_items:
        w = chip(d, x, y, item)
        x += w + 10
        if x > 500:
            x = 92
            y += 44
    rounded_box(d, (636, 170, 1290, 614))
    d.text((664, 204), "Scraping / collection methods", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        664,
        250,
        [
            "LinkedIn: Apify cloud scraper",
            "Staff.am and job.am: requests + BeautifulSoup",
            "EPAM: internal search API",
            "Picsart / DISQO: public ATS APIs",
            "DataArt / ServiceTitan: Playwright for dynamic content",
            "SoftConstruct / Krisp / Synopsys: server-rendered HTML parsing",
        ],
        560,
    )
    d.text((664, 556), "Broad snapshot result: 1,369 postings from 14 sources", fill=DARK, font=F_STEP)
    footer(d, 4)
    return img


def slide_05():
    img, d = new_slide("Cleaning, Structuring, and IT-Only Filtering", "The broad market scrape had to be narrowed before downstream NLP analysis")
    rounded_box(d, (64, 178, 380, 620))
    d.text((98, 214), "IT-only funnel", fill=NAVY, font=F_SECTION)
    d.polygon([(142, 270), (302, 270), (250, 360), (194, 360)], fill=SOFT_AMBER, outline=LINE)
    d.text((176, 292), "1,369", fill=DARK, font=F_BIG)
    d.text((168, 354), "Broad jobs", fill=GRAY, font=F_SMALL)
    d.polygon([(174, 390), (270, 390), (246, 458), (198, 458)], fill=SOFT_TEAL, outline=LINE)
    d.text((202, 407), "58", fill=DARK, font=F_NUM)
    d.text((192, 446), "Review", fill=GRAY, font=F_SMALL)
    d.polygon([(192, 490), (252, 490), (238, 556), (206, 556)], fill=SOFT_BLUE, outline=LINE)
    d.text((204, 506), "753", fill=DARK, font=F_NUM)
    d.text((190, 546), "Keep for NLP", fill=GRAY, font=F_SMALL)
    rounded_box(d, (438, 178, 1290, 620))
    d.text((468, 214), "What happened in this step", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        468,
        260,
        [
            "Merged multiple raw schemas into one canonical dataset.",
            "Built a full_text field for downstream text analysis.",
            "Removed repeated boilerplate from job descriptions.",
            "Created a keep / drop / review audit for IT-only filtering.",
            "Preserved the broad market snapshot for transparency, but used the IT-only subset for analysis.",
        ],
        760,
    )
    d.text((468, 528), "Why this matters", fill=DARK, font=F_STEP)
    d.text((468, 560), "Without this step, non-IT and mixed-role postings would distort the demand-side skill signal.", fill=GRAY, font=F_BODY)
    footer(d, 5)
    return img


def slide_06():
    img, d = new_slide("Translation and Multilingual Handling", "YSU curriculum content had to be made comparable to the mostly English job corpus")
    rounded_box(d, (64, 182, 620, 610))
    d.text((96, 216), "Why translation was needed", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        96,
        266,
        [
            "YSU data is in Armenian, while most job postings are in English.",
            "A shared English pipeline is easier to validate and explain than a mixed-language pipeline.",
            "Translated text can still be inspected manually by a reviewer.",
        ],
        480,
    )
    rounded_box(d, (692, 182, 1290, 610))
    d.text((724, 216), "Provider comparison", fill=NAVY, font=F_SECTION)
    table(
        d,
        724,
        268,
        [270, 160],
        ["Provider", "Manual validation score"],
        [
            ["OpenAI gpt-4o-mini", "20 / 20"],
            ["Perplexity Sonar Pro", "6 / 20"],
        ],
        row_h=42,
    )
    d.text((724, 398), "Chosen solution", fill=DARK, font=F_STEP)
    draw_bullets(
        d,
        724,
        436,
        [
            "Translate Armenian curriculum text to English first.",
            "Keep technical terms preserved during translation.",
            "Use the translated output as the main NLP input.",
        ],
        500,
    )
    footer(d, 6)
    return img


def slide_07():
    img, d = new_slide("EDA and Data Understanding", "Exploratory analysis was used to understand asymmetry and corpus quality before NLP")
    rounded_box(d, (64, 174, 620, 614))
    d.text((96, 210), "Curriculum-side asymmetry", fill=NAVY, font=F_SECTION)
    labels = ["YSU", "AUA", "NUACA", "RAU"]
    values = [100, 97, 0, 0]
    hbars(d, 96, 258, labels, values, 100, 240, BLUE)
    d.text((96, 420), "Description availability drives concept richness.", fill=GRAY, font=F_BODY)
    d.text((96, 454), "AUA and YSU have much richer text for NLP than NUACA and RAU.", fill=GRAY, font=F_BODY)
    rounded_box(d, (724, 174, 1290, 614))
    d.text((756, 210), "Job-side structure", fill=NAVY, font=F_SECTION)
    hbars(d, 756, 258, ["LinkedIn", "EPAM", "Staff.am", "SoftConstruct"], [556, 71, 50, 37], 556, 210, TEAL)
    d.text((756, 426), "Main EDA finding", fill=DARK, font=F_STEP)
    draw_bullets(
        d,
        756,
        462,
        [
            "LinkedIn dominates the IT-only market subset.",
            "Company portals still add important employer-specific signal.",
            "The demand corpus is not uniform and must be interpreted carefully.",
        ],
        470,
    )
    footer(d, 7)
    return img


def slide_08():
    img, d = new_slide("TF-IDF Extraction: Frequency-Based Baseline", "Used as the main transparent baseline for candidate skill extraction")
    rounded_box(d, (64, 180, 590, 612))
    d.text((96, 216), "What TF-IDF means", fill=NAVY, font=F_SECTION)
    d.text((96, 270), "TF-IDF(term, document) = term frequency x inverse document frequency", fill=DARK, font=F_BODY)
    draw_bullets(
        d,
        96,
        330,
        [
            "Finds words or short phrases that are important inside one document relative to the full corpus.",
            "Transparent and easy to explain.",
            "Worked better than KeyBERT in validation against human skill tags.",
        ],
        450,
    )
    rounded_box(d, (700, 180, 1290, 612))
    d.text((732, 216), "Why it was used here", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        732,
        268,
        [
            "Strong baseline for technical vocabulary.",
            "Good at recovering repeated shared terms such as Python, SQL, cloud, testing.",
            "Useful for comparing curriculum and market vocabulary before normalization.",
        ],
        470,
    )
    d.text((732, 478), "Known weakness", fill=DARK, font=F_STEP)
    d.text((732, 514), "Can produce awkward fragments and generic terms if preprocessing is weak.", fill=GRAY, font=F_BODY)
    footer(d, 8)
    return img


def slide_09():
    img, d = new_slide("TF-IDF Example on My Data", "Example from the course: Information Technologies in the Professional Field (Python)")
    rounded_box(d, (64, 182, 540, 610))
    d.text((96, 218), "Input document", fill=NAVY, font=F_SECTION)
    lines = wrapped(
        d,
        "Application of the fundamentals of the Python programming language, working with data, variables, arrays, functions...",
        F_BODY,
        390,
    )
    cy = 274
    for line in lines:
        d.text((96, cy), line, fill=GRAY, font=F_BODY)
        cy += 24
    rounded_box(d, (620, 182, 672, 610), fill=SOFT_BLUE, shadow=False)
    d.text((631, 384), "->", fill=NAVY, font=F_BIG)
    rounded_box(d, (700, 182, 1290, 610))
    d.text((732, 218), "Top TF-IDF outputs", fill=NAVY, font=F_SECTION)
    tfidf_terms = ["python", "data", "language data variables", "arrays functions", "language data"]
    draw_bullets(d, 732, 272, tfidf_terms, 470, line_gap=14)
    d.text((732, 488), "Takeaway", fill=DARK, font=F_STEP)
    d.text((732, 524), "TF-IDF captured the main topic well, especially the core technology word 'python'.", fill=GRAY, font=F_BODY)
    footer(d, 9)
    return img


def slide_10():
    img, d = new_slide("KeyBERT Extraction: Semantic Phrase Method", "Used as a semantic comparison method against TF-IDF")
    rounded_box(d, (64, 180, 590, 612))
    d.text((96, 216), "What KeyBERT means", fill=NAVY, font=F_SECTION)
    d.text((96, 270), "Score(candidate phrase) = cosine similarity(document embedding, phrase embedding)", fill=DARK, font=F_BODY)
    draw_bullets(
        d,
        96,
        330,
        [
            "Uses embeddings to find phrases that are semantically close to the whole document.",
            "Produces richer multi-word phrases than TF-IDF.",
            "Useful for testing whether semantic extraction improves the alignment story.",
        ],
        450,
    )
    rounded_box(d, (700, 180, 1290, 612))
    d.text((732, 216), "Why it matters in this thesis", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        732,
        268,
        [
            "Captures meaning, not only frequency.",
            "Can recover more descriptive keyphrases from short course text.",
            "But raw overlap stays very low because these phrases rarely match job phrases exactly.",
        ],
        480,
    )
    footer(d, 10)
    return img


def slide_11():
    img, d = new_slide("KeyBERT Example on My Data", "Same course example used to compare semantic extraction with TF-IDF")
    rounded_box(d, (64, 182, 540, 610))
    d.text((96, 218), "Input document", fill=NAVY, font=F_SECTION)
    lines = wrapped(
        d,
        "Application of the fundamentals of the Python programming language, working with data, variables, arrays, functions...",
        F_BODY,
        390,
    )
    cy = 274
    for line in lines:
        d.text((96, cy), line, fill=GRAY, font=F_BODY)
        cy += 24
    rounded_box(d, (620, 182, 672, 610), fill=SOFT_TEAL, shadow=False)
    d.text((631, 384), "->", fill="#2c6b64", font=F_BIG)
    rounded_box(d, (700, 182, 1290, 610))
    d.text((732, 218), "Top KeyBERT outputs", fill=NAVY, font=F_SECTION)
    kb_terms = [
        "data visualization python",
        "visualization python teaching",
        "fundamentals python",
        "python teaching",
        "teaching create visualizations",
    ]
    draw_bullets(d, 732, 272, kb_terms, 470, line_gap=14)
    d.text((732, 490), "Takeaway", fill=DARK, font=F_STEP)
    d.text((732, 526), "KeyBERT gives richer phrases, but these phrases usually do not match job phrases directly as strings.", fill=GRAY, font=F_BODY)
    footer(d, 11)
    return img


def slide_12():
    img, d = new_slide("Validation, Sensitivity Analysis, and Noise Audit", "The NLP outputs were tested instead of being treated as automatic ground truth")
    rounded_box(d, (64, 180, 388, 612))
    d.text((92, 214), "1. Description asymmetry", fill=NAVY, font=F_STEP)
    table(d, 92, 256, [160, 100], ["AUA setup", "Coverage"], [["Names only", "1.3%"], ["Names + descriptions", "6.8%"]], row_h=42)
    d.text((92, 382), "Result: richer descriptions produce about a 5x multiplier.", fill=GRAY, font=F_SMALL)

    rounded_box(d, (494, 180, 882, 612))
    d.text((522, 214), "2. Human skill-tag validation", fill=NAVY, font=F_STEP)
    table(d, 522, 256, [160, 100, 100], ["Metric", "TF-IDF", "KeyBERT"], [["Soft recall", "44%", "21%"], ["Jobs with >=1 tag matched", "64.2%", "38.4%"]], row_h=42)
    d.text((522, 382), "Result: TF-IDF clearly outperformed KeyBERT on this validation set.", fill=GRAY, font=F_SMALL)

    rounded_box(d, (924, 180, 1290, 612))
    d.text((952, 214), "3. Noise audit", fill=NAVY, font=F_STEP)
    d.text((952, 274), "Initial TF-IDF overlap", fill=GRAY, font=F_SMALL)
    d.text((952, 302), "584 terms (12.6%)", fill=DARK, font=F_NUM)
    d.text((952, 372), "After stronger filtering + IT-only scoping", fill=GRAY, font=F_SMALL)
    d.text((952, 400), "279 terms (8.85%)", fill=DARK, font=F_NUM)
    d.text((952, 478), "Result: many apparent overlaps were generic English words, not real skills.", fill=GRAY, font=F_SMALL)
    footer(d, 12)
    return img


def slide_13():
    img, d = new_slide("ESCO Normalization: The Taxonomy Bridge", "This step turns different surface forms into comparable shared skill concepts")
    rounded_box(d, (64, 180, 620, 610))
    d.text((96, 216), "How it works", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        96,
        266,
        [
            "Encode extracted phrases and ESCO labels with the same embedding model.",
            "Compare them by cosine similarity.",
            "Keep matches above the calibrated threshold.",
            "Use ESCO concepts as the common comparison layer between curricula and jobs.",
        ],
        470,
    )
    d.text((96, 500), "Threshold calibration", fill=DARK, font=F_STEP)
    table(d, 96, 536, [180, 110], ["Item", "Value"], [["Calibration pairs", "293"], ["Selected threshold", "0.75"], ["Best F1", "0.711"]], row_h=34)

    rounded_box(d, (700, 180, 1290, 610))
    d.text((732, 216), "Example mapping", fill=NAVY, font=F_SECTION)
    table(
        d,
        732,
        268,
        [220, 290],
        ["Raw phrase", "ESCO concept"],
        [
            ["python programming", "Python (programming language)"],
            ["python development", "Python (programming language)"],
            ["object oriented programming", "object-oriented programming"],
            ["OOP principles", "object-oriented programming"],
        ],
        row_h=42,
    )
    d.text((732, 496), "Key message", fill=DARK, font=F_STEP)
    d.text((732, 532), "This step is what turns vocabulary overlap into concept overlap.", fill=GRAY, font=F_BODY)
    footer(d, 13)
    return img


def slide_14():
    img, d = new_slide("Before and After ESCO Normalization", "Concept-level alignment is much stronger than raw string overlap")
    rounded_box(d, (64, 182, 640, 610))
    d.text((96, 218), "Coverage comparison", fill=NAVY, font=F_SECTION)
    # Simple grouped bars
    items = [("TF-IDF", 8.85, 32.82, SOFT_BLUE, NAVY), ("KeyBERT", 0.33, 28.5, SOFT_TEAL, "#2c6b64")]
    base_x = 170
    for i, (label, pre, post, tint, accent) in enumerate(items):
        y = 310 + i * 130
        d.text((96, y + 26), label, fill=DARK, font=F_STEP)
        d.rounded_rectangle((190, y + 10, 520, y + 34), radius=12, fill="#ebedf1")
        d.rounded_rectangle((190, y + 10, 190 + int(pre / 35 * 330), y + 34), radius=12, fill=accent)
        d.text((530, y + 8), f"Pre-ESCO {pre}%", fill=GRAY, font=F_SMALL)
        d.rounded_rectangle((190, y + 54, 520, y + 78), radius=12, fill="#ebedf1")
        d.rounded_rectangle((190, y + 54, 190 + int(post / 35 * 330), y + 78), radius=12, fill=AMBER)
        d.text((530, y + 52), f"Post-ESCO {post}%", fill=GRAY, font=F_SMALL)
    rounded_box(d, (700, 182, 1290, 610))
    d.text((732, 218), "Interpretation", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        732,
        268,
        [
            "Raw string overlap severely underestimates real conceptual overlap.",
            "TF-IDF remains the stronger main method in this project.",
            "KeyBERT becomes more useful only after normalization.",
            "The ESCO-normalized metric is still a lower bound because ESCO misses many modern tools.",
        ],
        500,
    )
    footer(d, 14)
    return img


def slide_15():
    img, d = new_slide("Current Alignment Findings", "What the current pipeline shows about Armenian curricula and employer demand")
    rounded_box(d, (64, 180, 620, 614))
    d.text((96, 216), "Average coverage by university", fill=NAVY, font=F_SECTION)
    hbars(d, 96, 266, ["AUA", "YSU", "RAU", "NUACA"], [8.06, 5.96, 2.76, 2.52], 8.06, 250, BLUE)
    d.text((96, 450), "Best program: AUA Computer and Information Science (Master) - 12.27%", fill=GRAY, font=F_SMALL)
    d.text((96, 482), "Lowest current program: NUACA Geographic Information Systems (Master) - 0.92%", fill=GRAY, font=F_SMALL)
    rounded_box(d, (700, 180, 1290, 614))
    d.text((732, 216), "Top demanded skills in the IT-only market", fill=NAVY, font=F_SECTION)
    hbars(
        d,
        732,
        266,
        ["Python", "CI/CD", "AWS", "Azure", "GCP", "Docker"],
        [33.6, 31.1, 29.8, 26.3, 24.8, 22.1],
        33.6,
        220,
        TEAL,
    )
    d.text((732, 500), "Main finding", fill=DARK, font=F_STEP)
    d.text((732, 536), "Curricula overlap with the market more at the knowledge level than at the applied tool / workflow level.", fill=GRAY, font=F_BODY)
    footer(d, 15)
    return img


def slide_16():
    img, d = new_slide("Limitations and What I Will Do Next", "Tomorrow's presentation should show both the progress and the remaining gaps honestly")
    rounded_box(d, (64, 180, 620, 614))
    d.text((96, 216), "Main limitations", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        96,
        268,
        [
            "NPUA is still missing from the dataset.",
            "UFAR is still missing from the dataset.",
            "RAU is only partially covered.",
            "Description asymmetry remains strong across universities.",
            "ESCO misses modern tools such as Docker, React, Azure, Kubernetes, and CI/CD.",
        ],
        480,
    )
    rounded_box(d, (700, 180, 1290, 614))
    d.text((732, 216), "Immediate next steps", fill=NAVY, font=F_SECTION)
    draw_bullets(
        d,
        732,
        268,
        [
            "Try to get in touch with UFAR for curriculum data.",
            "Try to get in touch with NPUA for curriculum data.",
            "Try to contact or visit RAU to improve coverage beyond one program.",
            "Continue refining the thesis draft and interpretation chapters.",
        ],
        500,
    )
    d.text((732, 504), "How to frame this tomorrow", fill=DARK, font=F_STEP)
    d.text((732, 540), "The pipeline is complete and working; the next phase is improving data coverage and final interpretation.", fill=GRAY, font=F_BODY)
    footer(d, 16)
    return img


def build():
    slides = [
        slide_01(),
        slide_02(),
        slide_03(),
        slide_04(),
        slide_05(),
        slide_06(),
        slide_07(),
        slide_08(),
        slide_09(),
        slide_10(),
        slide_11(),
        slide_12(),
        slide_13(),
        slide_14(),
        slide_15(),
        slide_16(),
    ]
    paths = save_slides(slides)
    print(PDF_PATH)
    for p in paths:
        print(p)


if __name__ == "__main__":
    build()
