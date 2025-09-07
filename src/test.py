"""
Collect a small AI-jobs dataset from three sources:
- Adzuna (aggregator; requires APP_ID/APP_KEY env vars)
- Ashby (per-organization job board; e.g., OpenAI)
- Greenhouse (per-organization job board; e.g., Anthropic, Scale AI)

Outputs a deduplicated JSONL file: sample_jobs.jsonl

This script keeps the footprint tiny (one request per source by default)
and normalizes fields to a common schema suitable for later vectorization.
"""
from __future__ import annotations

import os
import re
import json
import time
import hashlib
import html
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()
# ---------------------- Config ----------------------
# Tune these to your taste
ADZUNA_COUNTRIES = ["us", "gb"]  # keep small for demo
ADZUNA_RESULTS_PER_PAGE = 25
ADZUNA_QUERY = (
    '"machine learning" OR "artificial intelligence" OR AI OR "ML" OR "deep learning" '
    'OR "data scientist" OR "MLE" OR "LLM" OR "NLP"'
)

ASHBY_ORGS = [
    "openai",  # add more org slugs if you know them
]

GREENHOUSE_BOARDS = [
    "anthropic",
    "scaleai",
    "xai",
]

AI_KEYWORDS = [
    r"\bAI\b",
    r"\bML\b",
    r"machine\s+learning",
    r"artificial\s+intelligence",
    r"deep\s+learning",
    r"LLM",
    r"NLP",
    r"data\s+scientist",
    r"(ML|AI)\s+engineer",
    r"(research|applied)\s+(scientist|engineer)",
]
AI_RE = re.compile("|".join(AI_KEYWORDS), flags=re.I)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html;q=0.8,*/*;q=0.5",
}

TIMEOUT = 15
SLEEP_BETWEEN_CALLS = 0.6  # be polite even with public APIs
OUTPUT_PATH = "sample_jobs.jsonl"

# ---------------------- Helpers ----------------------

def parse_dt(s: Optional[str]) -> Optional[str]:
    """Parse many ISO-ish timestamps to ISO 8601 (UTC if possible). Return None if unknown."""
    if not s:
        return None
    # Normalize Z suffix
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        return dt.isoformat()
    except Exception:
        return None


def strip_html(text: Optional[str]) -> str:
    if not text:
        return ""
    # Remove HTML tags quickly; for production consider Bleach/BS4
    no_tags = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", no_tags)).strip()


def is_ai_role(title: str, description: str) -> bool:
    blob = f"{title}\n{description}"
    return bool(AI_RE.search(blob))


def dedupe_key(company: str, title: str, location: Optional[str], url: Optional[str]) -> str:
    canonical = f"{(company or '').strip().lower()}|{(title or '').strip().lower()}|{(location or '').strip().lower()}|{(url or '').strip().lower()}"
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()


# ---------------------- Source: Adzuna ----------------------

# def fetch_adzuna(max_results: int = 50) -> List[Dict[str, Any]]:
#     app_id = os.getenv("ADZUNA_APP_ID")
#     app_key = os.getenv("ADZUNA_APP_KEY")
#     print(f"[adzuna] Using APP_ID={app_id} APP_KEY={'*' * len(app_key) if app_key else None}")
#     if not app_id or not app_key:
#         print("[adzuna] Skipping (set ADZUNA_APP_ID/ADZUNA_APP_KEY to enable)")
#         return []

#     out: List[Dict[str, Any]] = []
#     for country in ADZUNA_COUNTRIES:
#         print(f"[adzuna] Fetching country: {country}")
#         if len(out) >= max_results:
#             print(f"[adzuna] Reached max_results={max_results}, stopping")
#             break
#         url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={app_key}"
#         params: dict[str, Any] = {
#             "app_id": app_id,
#             "app_key": app_key,
#             "what": ADZUNA_QUERY,
#             "results_per_page": ADZUNA_RESULTS_PER_PAGE,
#             "content-type": "application/json",
#         }
#         try:
#             resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
#             resp.raise_for_status()
#         except Exception as e:
#             print(f"[adzuna] {country} error: {e}")
#             continue
#         data = resp.json() or {}
#         print(f"[adzuna] {country} found {data.get('count', 0)} total jobs")
#         results = data.get("results", [])
#         for r in results:
#             company = (r.get("company") or {}).get("display_name") or ""
#             title = r.get("title") or ""
#             location = (r.get("location") or {}).get("display_name") or None
#             desc = r.get("description") or ""
#             if not is_ai_role(title, desc):
#                 continue
#             out.append(
#                 {
#                     "source": "adzuna",
#                     "source_id": str(r.get("id")),
#                     "company": company,
#                     "title": title,
#                     "locations": [location] if location else [],
#                     "remote": None,
#                     "posted_at": parse_dt(r.get("created")),
#                     "url": r.get("redirect_url"),
#                     "description": strip_html(desc),
#                     "tags": [((r.get("category") or {}).get("label") or "").strip()] if r.get("category") else [],
#                     "raw": r,
#                 }
#             )
#         time.sleep(SLEEP_BETWEEN_CALLS)
#     # cap
#     return out[:max_results]


# ---------------------- Source: Ashby (per org) ----------------------

def fetch_ashby(orgs: Iterable[str], max_results: int = 50) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for org in orgs:
        if len(out) >= max_results:
            break
        url = f"https://api.ashbyhq.com/posting-api/job-board/{org}"
        params = {"includeCompensation": "true"}
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json() or {}
        except Exception as e:
            print(f"[ashby] {org} error: {e}")
            continue

        # Ashby responses vary; common keys include 'jobs', 'jobPostings', or 'postings'
        postings = (
            data.get("jobs")
            or data.get("jobPostings")
            or data.get("postings")
            or []
        )
        for p in postings:
            print("processing posting:", p)
            title = p.get("title") or p.get("jobTitle") or ""
            company = org
            # location variants
            loc = (
                p.get("locationName")
                or p.get("location")
                or (p.get("locations") or [{}])[0].get("name") if p.get("locations") else None
            )
            desc = p.get("description") or p.get("jobDescription") or p.get("descriptionHtml") or ""
            url_post = p.get("applyUrl") or p.get("jobUrl") or p.get("jobUrl") or None
            if not is_ai_role(title, desc):
                continue
            out.append(
                {
                    "source": "ashby",
                    "source_id": str(p.get("id") or p.get("jobId") or p.get("guid") or ""),
                    "company": company,
                    "title": title,
                    "locations": [loc] if loc else [],
                    "remote": None,
                    "posted_at": parse_dt(p.get("publishedAt") or p.get("updatedAt") or p.get("createdAt")),
                    "url": url_post,
                    "description": strip_html(desc),
                    "tags": [t.get("name") for t in (p.get("teams") or []) if isinstance(t, dict)] if p.get("teams") else [],
                    'compensation': p.get("compensation") or p.get("salary") or None,
                    "raw": p,
                }
            )
        time.sleep(SLEEP_BETWEEN_CALLS)
    return out[:max_results]


# ---------------------- Source: Greenhouse (per board) ----------------------

def fetch_greenhouse(boards: Iterable[str], max_results: int = 50) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for board in boards:
        if len(out) >= max_results:
            break
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        params = {"content": "true"}
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json() or {}
        except Exception as e:
            print(f"[greenhouse] {board} error: {e}")
            continue
        jobs = data.get("jobs", [])
        for j in jobs:
            print("processing greenhouse job:", j)
            title = j.get("title") or ""
            company = board
            loc_obj = j.get("location") or {}
            location = loc_obj.get("name") if isinstance(loc_obj, dict) else None
            desc = j.get("content") or ""
            if not is_ai_role(title, desc):
                continue
            out.append(
                {
                    "source": "greenhouse",
                    "source_id": str(j.get("id")),
                    "company": company,
                    "title": title,
                    "locations": [location] if location else [],
                    "remote": None,
                    "posted_at": parse_dt(j.get("updated_at") or j.get("created_at")),
                    "url": j.get("absolute_url"),
                    "description": strip_html(desc),
                    "tags": [d.get("name") for d in (j.get("departments") or []) if isinstance(d, dict)],
                    'compensation': p.get("compensation") or p.get("salary") or None,
                    "raw": j,
                }
            )
        time.sleep(SLEEP_BETWEEN_CALLS)
    return out[:max_results]


# ---------------------- Main orchestration ----------------------

def normalize_and_dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for it in items:
        company = (it.get("company") or "").strip()
        title = (it.get("title") or "").strip()
        loc = (it.get("locations") or [None])[0]
        url = it.get("url")
        key = dedupe_key(company, title, loc, url)
        if key in seen:
            continue
        seen.add(key)
        # Keep only normalized fields; leave raw for auditing
        out.append(
            {
                "id": key,
                "source": it.get("source"),
                "source_id": it.get("source_id"),
                "company": company,
                "title": title,
                "locations": it.get("locations") or [],
                "remote": it.get("remote"),
                "posted_at": it.get("posted_at"),
                "url": url,
                "description": it.get("description") or "",
                "tags": it.get("tags") or [],
                "source_payload": it.get("raw"),
            }
        )
    return out


def main() -> None:
    all_items: List[Dict[str, Any]] = []

    # print("Fetching Adzuna…")
    # all_items.extend(fetch_adzuna(max_results=40))

    print("Fetching Ashby…")
    all_items.extend(fetch_ashby(ASHBY_ORGS, max_results=40))

    # print("Fetching Greenhouse…")
    all_items.extend(fetch_greenhouse(GREENHOUSE_BOARDS, max_results=60))

    print(f"Fetched raw items: {len(all_items)}")

    normalized = normalize_and_dedupe(all_items)
    print(f"After normalization/dedupe: {len(normalized)} items")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in normalized:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Show a small sample
    print("\nSample:")
    for item in normalized[:5]:
        print(json.dumps({k: item[k] for k in ["company", "title", "locations", "url"]}, ensure_ascii=False))

    print(f"\nWrote {len(normalized)} jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
