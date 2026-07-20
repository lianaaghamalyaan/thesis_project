"""IT-job classification: is this posting IT-relevant, and if so, which role
group? Ported verbatim from notebooks/3_analysis/00_filter_it_jobs.ipynb (not
modified — see CLAUDE.md) so weekly automation can call the exact same
rule-based classifier that produced final_jobs_dataset_it_only.csv, instead
of a second, drifting reimplementation. Pure regex/keyword rules, no ML — a
deliberate choice made in the original notebook so the decision is auditable
and reproducible without an API key.

classify_job() returns one of three decisions:
  "keep"   — confidently IT, with a role group.
  "drop"   — confidently not IT.
  "review" — ambiguous; needs a human decision (see the review-queue pattern
             used throughout data/runs/*/july_2026_review_queue*.csv this
             repo already established) rather than silently guessing either
             way.
"""
from __future__ import annotations

import re

ROLE_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "Backend",
        [
            r"\bbackend\b", r"\bback\s*-?end\b", r"\bsoftware engineer\b", r"\bsoftware developer\b",
            r"\bsoftware engineering\b",
            r"\bpython developer\b", r"\bpython engineer\b", r"\bjava developer\b", r"\bjava engineer\b",
            r"\b\.net developer\b", r"\b\.net engineer\b", r"\bc# developer\b", r"\bc# engineer\b",
            r"\bnode(?:\.js|js)?\b", r"\bphp\b", r"\bgolang\b", r"\brust engineer\b", r"\bruby\b",
            r"\bscala\b", r"\bkernel developer\b", r"\bapi developer\b", r"\bhtml/markup developer\b",
            r"\bmarkup developer\b", r"\bwebflow developer\b", r"\bdelphi developer\b", r"\blaravel\b",
            r"\bsapui5\b", r"\bfiori developer\b", r"\bhtml5 game developer\b",
            r"\bc\s*/\s*c\+\+\s+engineer\b", r"\bunity developer\b", r"\bsearch engineer\b",
            r"\bintegrations engineer\b", r"\bautomation engineer\b", r"\bproduct engineer\b",
            r"\b1c\b", r"\b1c erp\b", r"\b1c developer\b", r"\b1c specialist\b",
        ],
    ),
    (
        "Frontend / JS",
        [
            r"\bfrontend\b", r"\bfront\s*-?end\b", r"\breact\b", r"\bangular\b", r"\bvue\b",
            r"\bjavascript\b", r"\btypescript\b", r"\bui developer\b", r"\bweb developer\b",
        ],
    ),
    ("Full Stack", [r"\bfull\s*-?stack\b", r"\bfullstack\b"]),
    (
        "Mobile",
        [
            r"\bandroid\b", r"\bios\b", r"\bmobile developer\b", r"\bmobile engineer\b",
            r"\bflutter\b", r"\breact native\b", r"\bswift\b", r"\bkotlin\b",
        ],
    ),
    (
        "Data / ML / AI",
        [
            r"\bdata engineer\b", r"\bdata scientist\b", r"\bdata analyst\b", r"\bml engineer\b",
            r"\bmachine learning\b", r"\bartificial intelligence\b", r"\bai engineer\b", r"\bgenai\b",
            r"\bnlp\b", r"\bcomputer vision\b", r"\bbi developer\b", r"\bpower bi developer\b",
            r"\bbi engineer\b", r"\bdata specialist\b", r"\bdata quality analyst\b", r"\bdata ops\b",
            r"\bsystem analyst\b", r"\bbusiness systems analyst\b", r"\bdata architect\b",
            r"\benterprise architecture\b",
        ],
    ),
    (
        "DevOps / Cloud",
        [
            r"\bdevops\b", r"\bsre\b", r"\bsite reliability\b", r"\bcloud\b",
            r"\bplatform engineer\b", r"\bplatform release engineer\b", r"\brelease engineer\b",
            r"\bdeployment engineer\b", r"\binfrastructure\b", r"\bbuild engineer\b",
            r"\bdatabase reliability engineer\b", r"\bdbre\b",
        ],
    ),
    (
        "QA / Testing",
        [
            r"\bqa\b", r"\bquality assurance\b", r"\btest automation\b", r"\btester\b",
            r"\bsdet\b", r"\bsqa\b", r"\baqa\b", r"\bquality engineer\b", r"\btest engineer\b",
            r"\bsoftware engineer in test\b", r"\bfunctional testing\b",
        ],
    ),
    (
        "Security",
        [
            r"\bsecurity\b", r"\bcyber", r"\binfosec\b", r"\bsoc analyst\b",
            r"\bpenetration\b", r"\bvulnerability\b", r"\bokta administrator\b",
        ],
    ),
    (
        "IT Support / Admin",
        [
            r"\bit support\b", r"\btechnical support engineer\b", r"\bfrontline support engineer\b",
            r"\bend-user support engineer\b", r"\bapplication support engineer\b",
            r"\bmiddleware support engineer\b", r"\btechnical support team lead\b",
            r"\bservice desk\b", r"\bservicedesk engineer\b", r"\bsystem administrator\b",
            r"\bdatabase administrator\b", r"\bnetwork administrator\b", r"\bjira administrator\b",
            r"\bcorporate applications administrator\b", r"\bgoogle workspace deployment engineer\b",
            r"\bdata center technician\b", r"\bendpoint operations technician\b", r"\bnoc engineer\b",
            r"\bcustomer support\b", r"\bcustomer support engineer\b",
            r"\bcustomer success\b", r"\bcustomer success manager\b",
            r"\bmember support\b", r"\bbitrix",
        ],
    ),
    (
        "Hardware / Embedded",
        [
            r"\bembedded\b", r"\bfirmware\b", r"\bhardware\b", r"\bfpga\b", r"\basic\b",
            r"\bvlsi\b", r"\brtl\b", r"\bverilog\b", r"\bvhdl\b", r"\bpcb\b",
            r"\bphysical design engineer\b", r"\bdesign verification\b", r"\bmbist\b",
            r"\bdft\b", r"\bsta\b", r"\bcad\/methodology\b", r"\banalog layout\b",
            r"\bcharacterization engineer\b", r"\br&d engineer\b",
        ],
    ),
    (
        "Technical Management",
        [
            r"\bengineering manager\b", r"\bdirector,\s*software engineering\b",
            r"\bplatform engineering team lead\b", r"\bengineering technical leader\b",
            r"\bengineering team lead\b", r"\bengineering team leader\b",
            r"\btechnical project manager\b", r"\bbackend team lead\b", r"\bqa team lead\b",
            r"\bteam lead back-end developer\b", r"\bhead of .*enterprise architecture\b",
            r"\bsenior technical manager\b", r"\bsolution architect\b", r"\bsolutions architect\b",
        ],
    ),
    (
        "UX / Product Design",
        [
            r"\bproduct designer\b", r"\bux designer\b", r"\bui/ux designer\b",
            r"\bux/ui designer\b", r"\bux engineer\b", r"\binteraction designer\b",
        ],
    ),
]

DROP_PATTERNS = [
    r"\bmarketing\b", r"\bmedia\b", r"\bpublic relations\b", r"\bpr specialist\b",
    r"\bseo\b", r"\bsales\b", r"\baccount manager\b", r"\bbusiness development\b",
    r"\brecruit", r"\bhr\b", r"\bhuman resources\b", r"\btalent acquisition\b",
    r"\bpeople analytics\b", r"\blegal\b", r"\bcompliance\b", r"\bprocurement\b",
    r"\blogistics\b", r"\bfinance\b", r"\bfinancial\b", r"\baccountant\b",
    r"\bbilling\b", r"\bhotel\b", r"\binterior architect\b", r"\binterior designer\b",
    r"\bgraphic\b", r"\billustrator\b", r"\banimator\b", r"\bartist\b",
    r"\bmotion designer\b", r"\bux researcher\b",
    r"\bgraphic designer\b", r"\bvisual designer\b", r"\bproducer\b", r"\bteacher\b", r"\btrainer\b",
    r"\bsupport representative\b",
    r"\bmerchant risk analyst\b", r"\bpayroll analyst\b", r"\bchargeback\b",
    r"\bstrategy associate\b", r"\bgrowth specialist\b",
]

STRONG_TECH_HINT_WORDS = [
    "engineer", "developer", "administrator", "architect", "platform", "software",
    "system", "database", "network", "security", "cloud", "devops", "qa", "test",
    "data", "ml", "ai", "frontend", "backend", "full stack", "mobile", "support",
    "embedded", "firmware", "hardware",
]

AMBIGUOUS_BUSINESS_HINTS = [
    "analyst", "manager", "product", "owner", "consultant", "specialist", "audit", "intern", "interviewer",
]

TECH_TEXT_TERMS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue", "node", "php",
    "sql", "database", "api", "microservice", "docker", "kubernetes", "aws", "azure", "gcp",
    "linux", "git", "ci/cd", "terraform", "ansible", "jenkins", "pytest", "selenium",
    "playwright", "postman", "machine learning", "data science", "data engineer", "power bi",
    "tableau", "firmware", "embedded", "asic", "fpga", "vlsi", "verilog", "vhdl", "rtl",
    "soc", "security", "encryption", "network", ".net", "c#", "c++", "golang", "swift",
    "kotlin", "android", "ios", "jira", "okta", "1c",
]

COMPILED_ROLE_PATTERNS = [
    (role, [re.compile(p, re.IGNORECASE) for p in patterns])
    for role, patterns in ROLE_PATTERNS
]
COMPILED_DROP_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DROP_PATTERNS]


def normalize_text(value: object) -> str:
    # Missing text in a pandas row (float('nan')) is truthy, so `value or ""`
    # doesn't catch it — must check the type explicitly, not just falsiness.
    if not isinstance(value, str):
        return ""
    return " ".join(value.lower().split())


def match_role(title: str) -> str | None:
    for role, patterns in COMPILED_ROLE_PATTERNS:
        if any(p.search(title) for p in patterns):
            return role
    return None


def match_drop_reason(title: str) -> str | None:
    for p in COMPILED_DROP_PATTERNS:
        if p.search(title):
            return p.pattern
    return None


def tech_text_score(text: str) -> int:
    return sum(term in text for term in TECH_TEXT_TERMS)


def has_strong_tech_hint(title: str) -> bool:
    return any(word in title for word in STRONG_TECH_HINT_WORDS)


def has_ambiguous_business_hint(title: str) -> bool:
    return any(word in title for word in AMBIGUOUS_BUSINESS_HINTS)


def classify_job(job_title: str, full_text: str) -> tuple[str, str, str, int]:
    """Returns (decision, role, reason, tech_text_score). decision is one of
    "keep" / "drop" / "review"; role is "Non-IT" for dropped postings,
    "Ambiguous" for ones flagged for review with no clear role guess."""
    title = normalize_text(job_title)
    text = normalize_text(full_text)[:5000]

    role = match_role(title)
    drop_reason = match_drop_reason(title)
    score = tech_text_score(text)

    if role:
        if role == "Technical Management" and score < 2:
            return "review", role, "title matched Technical Management but text support was weak", score
        if role == "Data / ML / AI" and drop_reason:
            return "review", role, f"title matched {role} but also matched exclusion pattern {drop_reason}", score
        if drop_reason and score < 2 and role not in {"Data / ML / AI", "Technical Management"}:
            return "drop", "Non-IT", f"title matched exclusion pattern {drop_reason}", score
        return "keep", role, f"title matched {role}", score

    if drop_reason:
        return "drop", "Non-IT", f"title matched exclusion pattern {drop_reason}", score

    if score >= 3 and has_strong_tech_hint(title) and has_ambiguous_business_hint(title):
        return "review", "Ambiguous", f"title mixed technical and business cues with {score} technical text signals", score
    if score >= 4 and has_strong_tech_hint(title):
        return "keep", "General IT", f"text had {score} technical signals", score
    if score >= 2 and has_strong_tech_hint(title):
        return "review", "Ambiguous", f"title was technical-ish and text had {score} technical signals", score

    return "drop", "Non-IT", f"no strong IT title pattern and only {score} technical text signals", score
