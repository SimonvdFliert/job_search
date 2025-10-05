from __future__ import annotations
from fastapi.responses import JSONResponse
from src.settings import settings
from src.services.embedding import embedding_service
from src.services.search import search_service
from src.services.insertion import db_insertion_service
from src.services.scrapers import scraper_service
from src.database import database_service
from collections import Counter

def do_job_search(search_params: dict) -> JSONResponse | dict | ValueError:
    q = search_params.get("q", None)
    top_k = search_params.get("top_k", 20)
    mode = search_params.get("mode", "semantic")

    if not q:
        return JSONResponse({"results": [], "took_ms": 0})
    vec = embedding_service.embed_texts([q])[0]

    match mode:
        case "semantic":
            return search_service.search_semantic(vec, top_k=top_k)
        case "hybrid":
            return search_service.search_hybrid(vec, top_k=top_k, q_text=q)
        case _:
            raise ValueError(f"Unknown search mode: {mode}")

def scrape_jobs() -> None:
    print("Starting scraping jobs...")
    batch = []
    if settings.scrape.ASHBY_ORGS: batch += scraper_service.fetch_ashby(settings.scrape.ASHBY_ORGS)
    if settings.scrape.GREENHOUSE_BOARDS: batch += scraper_service.fetch_greenhouse(settings.scrape.GREENHOUSE_BOARDS)
    n = db_insertion_service.insert_jobs_into_db(batch)
    embedding_service.embed_data()
    print(f"ingested {n} rows")

def get_job_by_id(job_id: str):
    with database_service.get_db_context() as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()

    return row


def get_statistics(top_n_companies: int = 10) -> dict:
    """
    Builds all datasets using CTEs in a single query.
    Returns:
      - jobs_per_day: [{date, count}]
    - jobs_per_country: [{country, count}]
    - top_companies: [{company, count}]
    - company_offer_type: [{company, engineer, other}]
    - job_types: [{type, count}]
    """
    with database_service.get_db_context() as cur:
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
                (SELECT row_to_json(ss) FROM stats_summary ss) AS stats_summary
        """)
        result = cur.fetchone()

        stats = {
            "jobs_per_day": result["jobs_per_day"] or [],
            "top_companies": result["top_companies"] or [],
            "company_offer_type": result["company_offer_type"] or [],
            "stats_summary": result.get("stats_summary") or {}
            }
        
        formatted_countries = []
        if result["jobs_per_country"]:
            formatted_countries = format_jobs_per_country(result["jobs_per_country"])

        stats["jobs_per_location"] = formatted_countries


    return stats

def format_jobs_per_country(raw_data: list[dict]) -> list[dict]:
    country_counts = Counter()
    for item in raw_data:
        if '|' in item['country'] or ';' in item['country']:
            countries = [c.strip().upper() for c in item['country'].replace(';', '|').split('|')]
            for country in countries:
                country_counts[country] += item['count']
        else:
            country = item['country'].strip().upper()
            if country:
                country_counts[country] += item['count']

    formatted = [
        {"country": country, "count": count}
        for country, count in country_counts.most_common()  # most_common() returns sorted
    ]
    return formatted