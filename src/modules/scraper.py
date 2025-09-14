from __future__ import annotations

import re
import time
import hashlib
import html
from typing import Any, Dict, Iterable, List, Optional
from datetime import datetime
import requests
from src.modules.settings import settings
from src.modules.settings import AI_RE

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

def fetch_ashby(orgs: Iterable[str], max_results: int = 50) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    print('orgs:', orgs)
    for org in orgs:
        if len(out) >= max_results:
            print('reached max results:', max_results)
            break
        print(f'fetching org: {org}')
        request_headers = {
            "User-Agent": settings.scrape.headers
        }

        url = f"https://api.ashbyhq.com/posting-api/job-board/{org}"
        params = {"includeCompensation": "true"}
        try:
            print('requesting URL:', url, 'with params:', params)
            resp = requests.get(url, params=params, headers=request_headers, timeout=settings.scrape.time_out)
            print('response status code:', resp.status_code)
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

        # print('postings:', postings)

        for p in postings:
            # print("processing posting:", p)
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
        time.sleep(settings.scrape.sleep_between_calls)
    return out[:max_results]


# ---------------------- Source: Greenhouse (per board) ----------------------

def fetch_greenhouse(boards: Iterable[str], max_results: int = 50) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for board in boards:
        if len(out) >= max_results:
            break
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        params = {"content": "true"}
        request_headers = {
            "User-Agent": settings.scrape.headers
        }
        try:
            resp = requests.get(url, params=params, headers=request_headers, timeout=settings.scrape.time_out)
            resp.raise_for_status()
            data = resp.json() or {}
        except Exception as e:
            print(f"[greenhouse] {board} error: {e}")
            continue
        jobs = data.get("jobs", [])
        for j in jobs:
            # print("processing greenhouse job:", j)
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
                    'compensation': j.get("compensation") or j.get("salary") or None,
                    "raw": j,
                }
            )
        time.sleep(settings.scrape.sleep_between_calls)
    return out[:max_results]


# def normalize_and_dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # seen = set()
    # out: List[Dict[str, Any]] = []
    # for it in items:
    #     company = (it.get("company") or "").strip()
    #     title = (it.get("title") or "").strip()
    #     loc = (it.get("locations") or [None])[0]
    #     url = it.get("url")
    #     key = dedupe_key(company, title, loc, url)
    #     if key in seen:
    #         continue
    #     seen.add(key)
    #     # Keep only normalized fields; leave raw for auditing
    #     out.append(
    #         {
    #             "id": key,
    #             "source": it.get("source"),
    #             "source_id": it.get("source_id"),
    #             "company": company,
    #             "title": title,
    #             "locations": it.get("locations") or [],
    #             "remote": it.get("remote"),
    #             "posted_at": it.get("posted_at"),
    #             "url": url,
    #             "description": it.get("description") or "",
    #             "tags": it.get("tags") or [],
    #             "source_payload": it.get("raw"),
    #         }
    #     )
    # return out