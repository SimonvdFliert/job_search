from __future__ import annotations
import argparse, os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

from src.modules.settings import settings
from src.modules.database import ensure_database_exists, apply_schema, get_cursor
from src.modules.embeddings import embed_texts
from src.modules import scraper
from . import api_services as svc
from starlette.middleware.cors import CORSMiddleware
from collections import Counter, defaultdict
from datetime import date
from typing import Any, Dict, Iterable, List, Set, Tuple
import zoneinfo
from datetime import datetime

# TZ = zoneinfo.ZoneInfo()

app = FastAPI(title="Jobs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()
    if not row: raise HTTPException(404, "not found")
    return row

@app.get("/search")
def search(q: str = Query(""), top_k: int = Query(20, le=100), mode: str = Query("semantic")):
    if not q:
        return JSONResponse({"results": [], "took_ms": 0})
    print('search q:', q)
    vec = embed_texts([q])[0]
    # print('vector len:', len(vec))
    print('vector:', vec)
    rows = svc.search_semantic(vec, top_k=top_k) if mode == "semantic" else svc.search_hybrid(vec, q_text=q, top_k=top_k)
    return {"results": rows}

@app.get('/statistics/job_post_date')
def job_post_date_stats():
    """"
    Returns all the job postings that are active
    """
    with get_cursor() as cur:
        cur.execute("""
            SELECT DATE(posted_at) AS post_date, COUNT(*) AS count
            FROM jobs
            WHERE posted_at IS NOT NULL
            GROUP BY post_date
            """)
        rows = cur.fetchall()
    return {"results": rows}


@app.get("/statistics/CTE")
def statistics_cte(top_n_companies: int = 10):
    """
    Builds all datasets using CTEs in a single query.
    Returns:
      - jobs_per_day: [{date, count}]
    - jobs_per_country: [{country, count}]
    - top_companies: [{company, count}]
    - company_offer_type: [{company, engineer, other}]
    - job_types: [{type, count}]
    """

    company_counts = Counter()


    with get_cursor() as cur:
        cur.execute(f"""
            WITH active_jobs AS (
                SELECT
                    id,
                    (posted_at)::date AS posting_date,
                    locations,
                    company,
                    title
                FROM jobs
                WHERE posted_at >= now() - interval '30 days'
            ),
            jobs_per_day AS (
                SELECT posting_date AS date, COUNT(*) AS count
                FROM active_jobs
                WHERE posting_date IS NOT NULL
                GROUP BY posting_date
            ),
            jobs_per_country AS (
                SELECT country, COUNT(*) AS count
                FROM (
                    SELECT DISTINCT id, unnest(
                        ARRAY(SELECT jsonb_array_elements_text(locations))
                    ) AS country
                    FROM active_jobs
                ) AS subquery
                WHERE country IS NOT NULL AND country <> ''
                GROUP BY country
            ),
            top_companies AS (
                SELECT company AS company, COUNT(*) AS count
                FROM active_jobs
                WHERE company IS NOT NULL AND company <> ''
                GROUP BY company
                ORDER BY count DESC
                LIMIT {top_n_companies}
            ),
            stats_summary AS (
                SELECT 
                    -- Total active jobs (last 30 days)
                    COUNT(DISTINCT id) as total_active_jobs,
                    
                    -- Total companies with active jobs
                    COUNT(DISTINCT company) as total_active_companies,
                    
                    -- Most recent job posting
                    MAX(posting_date) as latest_job_date
                FROM active_jobs
                WHERE company IS NOT NULL AND company <> ''
                ),
            company_offer_type AS (
                SELECT 
                    company,
                    SUM(CASE WHEN UPPER(title) ~* 'ENGINEER|DEVELOPER|SOFTWARE|SWE|DEVOPS|DATA ENGINEER|ML ENGINEER' THEN 1 ELSE 0 END) AS engineer,
                    SUM(CASE WHEN NOT (UPPER(title) ~* 'ENGINEER|DEVELOPER|SOFTWARE|SWE|DEVOPS|DATA ENGINEER|ML ENGINEER') THEN 1 ELSE 0 END) AS other,
                    COUNT(*) AS total
                FROM active_jobs
                WHERE company IS NOT NULL AND company <> ''
                GROUP BY company
                ORDER BY total DESC
                LIMIT {top_n_companies}
            )
            SELECT 
                (SELECT jsonb_agg(jpd ORDER BY jpd.date) FROM jobs_per_day jpd) AS jobs_per_day,
                (SELECT jsonb_agg(jpc ORDER BY jpc.count DESC) FROM jobs_per_country jpc) AS jobs_per_country,
                (SELECT jsonb_agg(tc) FROM top_companies tc) AS top_companies,
                (SELECT jsonb_agg(cot) FROM company_offer_type cot) AS company_offer_type,
                (SELECT row_to_json(ss) FROM stats_summary ss) AS summary
        """)
        result = cur.fetchone()

        stats = {
            "jobs_per_day": result["jobs_per_day"] or [],
            # "jobs_per_country": result["jobs_per_country"] or [],
            "top_companies": result["top_companies"] or [],
            "company_offer_type": result["company_offer_type"] or [],
            "stats_summary": result.get("summary") or {}
            }
        
        if result["jobs_per_country"]:
            for item in result["jobs_per_country"]:
                if '|' or ';' in item['country']:
                    countries = [c.strip().upper() for c in item['country'].replace(';', '|').split('|')]
                    for country in countries:
                        company_counts[country] += item['count']

        jobs_per_location = [
            {"location": loc, "count": count}
            for loc, count in company_counts.most_common()  # most_common() returns sorted
        ]

        # Add to your result
        stats["jobs_per_location"] = jobs_per_location


    return stats


















@app.get("/statistics/summary")
def statistics_summary(top_n_companies: int = 12):
    """
    Builds all datasets in one pass over active jobs.
    Returns:
      - jobs_per_day: [{date, count}]
      - jobs_per_country: [{country, count}]
      - top_companies: [{company, count}]
      - company_offer_type: [{company, engineer, other}]
      - job_types: [{type, count}]
    """
    jobs_per_day = Counter()
    jobs_per_country = Counter()
    company_counts = Counter()
    company_role_breakdown = defaultdict(lambda: Counter({"Engineer": 0, "Other": 0}))
    job_types = Counter()

    with get_cursor() as cur:
        cur.execute("""
            SELECT
            id,
            (posted_at)::date AS posting_date,  -- alias it!
            locations,
            company,
            title
            FROM jobs
            WHERE is_active = TRUE
        """)

        while True:
            rows = cur.fetchmany(100)
            if not rows:
                break

            for row in rows:  # row is dict-like
                id_ = row["id"]
                posting_date = row["posting_date"]   # this is a datetime.date
                locations = row["locations"]
                company = row["company"]
                title = row["title"]

                # 1) Line chart (by day)
                if posting_date:
                    jobs_per_day[posting_date if isinstance(posting_date, date) else datetime.strptime(posting_date, '%Y-%m-%d').date()] += 1

                # 2) Heatmap per country (dedupe per job per country)
                for country in extract_countries(locations):
                    jobs_per_country[country] += 1

                # 3) Top companies
                comp = normalize_str(company)
                if comp:
                    company_counts[comp] += 1

                    # 4) Company offer type (Engineer vs Other, based on title)
                    role = classify_role(title or "")
                    company_role_breakdown[comp][role] += 1

                # # 5) Pie of job type (Remote / Intern / Contract / Full-Time/Other)
                # job_types[classify_job_type({
                #     "is_remote": is_remote, "is_intern": is_intern, "is_contract": is_contract
                # })] += 1

    # Prepare payloads for charts

    jobs_per_day_series = [
        {"date": d.isoformat(), "count": c}
        for d, c in sorted(jobs_per_day.items())
    ]

    jobs_per_country_series = [
        {"country": k, "count": v}
        for k, v in jobs_per_country.most_common()
    ]

    top_companies_series = [
        {"company": k, "count": v}
        for k, v in company_counts.most_common(top_n_companies)
    ]

    company_offer_type_series = []
    for company_name, counts in company_role_breakdown.items():
        company_offer_type_series.append({
            "company": company_name,
            "engineer": int(counts["Engineer"]),
            "other": int(counts["Other"]),
            "total": int(counts["Engineer"] + counts["Other"]),
        })
    # Keep only the top N by total to match the bar chart
    company_offer_type_series.sort(key=lambda x: x["total"], reverse=True)
    company_offer_type_series = company_offer_type_series[:top_n_companies]

    job_types_series = [{"type": k, "count": v} for k, v in job_types.items()]

    return {
        "jobs_per_day": jobs_per_day_series,
        "jobs_per_country": jobs_per_country_series,
        "top_companies": top_companies_series,
        "company_offer_type": company_offer_type_series,
        # "job_types": job_types_series,
    }



def cmd_bootstrap():
    ensure_database_exists()
    apply_schema()
    print("bootstrap complete")

def cmd_ingest():
    batch = []
    if settings.scrape.ASHBY_ORGS: batch += scraper.fetch_ashby(settings.scrape.ASHBY_ORGS)
    if settings.scrape.GREENHOUSE_BOARDS: batch += scraper.fetch_greenhouse(settings.scrape.GREENHOUSE_BOARDS)
    n = svc.upsert_jobs(batch)
    print(f"ingested {n} rows")

def cmd_embed():
    # simple loop until no more rows
    total = 0
    while True:
        todo = svc.fetch_missing_embeddings(limit=settings.model.BATCH_SIZE * 4)
        if not todo: break
        ids, texts = zip(*todo)
        vecs = embed_texts(list(texts))
        total += svc.upsert_embeddings(list(zip(ids, vecs)))
    print(f"embedded {total} rows")

def cmd_api():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["bootstrap", "ingest", "embed", "api"])
    args = parser.parse_args()

    if args.mode == "bootstrap": cmd_bootstrap()
    elif args.mode == "ingest":  cmd_ingest()
    elif args.mode == "embed":   cmd_embed()
    elif args.mode == "api":     cmd_api()








def normalize_str(x: Any) -> str:
    return x.strip() if isinstance(x, str) else ""

def extract_countries(locations: Any) -> Set[str]:
    """
    locations: JSONB column; usually list[object|string], sometimes [] or NULL.
    Returns a set of uppercased country tokens per job (dedup within a job).
    Accepts elem like:
      {"countryCode":"NL"}, {"country":"Netherlands"}, "US", "United States"
    """
    if not locations:
        return set()
    elems: Iterable = locations if isinstance(locations, list) else [locations]
    out: Set[str] = set()
    for e in elems:
        val = None
        if isinstance(e, dict):
            val = e.get("countryCode") or e.get("country_code") or e.get("country") or e.get("countryName")
        elif isinstance(e, str):
            val = e
        if val:
            token = normalize_str(val).upper()
            if token:
                out.add(token)
    return out

ENGINEER_KEYWORDS = {"ENGINEER", "DEVELOPER", "SOFTWARE", "SWE", "DEVOPS", "DATA ENGINEER", "ML ENGINEER"}
def classify_role(title: str) -> str:
    t = normalize_str(title).upper()
    if not t:
        return "Other"
    return "Engineer" if any(k in t for k in ENGINEER_KEYWORDS) else "Other"

def classify_job_type(row: Dict[str, Any]) -> str:
    """
    Produces mutually exclusive types for the pie:
      Intern > Contract > Remote > Full-Time/Other
    Adjust this if remote should be orthogonal.
    """
    # If you don’t have these columns, you can infer via title keywords instead.
    is_intern   = bool(row.get("is_intern"))
    is_contract = bool(row.get("is_contract"))
    is_remote   = bool(row.get("is_remote"))
    if is_intern:   return "Intern"
    if is_contract: return "Contract"
    if is_remote:   return "Remote"
    return "Full-Time/Other"