from __future__ import annotations
from fastapi.responses import JSONResponse
from src.settings import settings
from src.embedding import embedding_service
from src.search import search_service
from src.insertion import db_insertion_service
from src.scrapers import scraper_service
from src.database import database_service
from collections import Counter
from sqlalchemy import text

def do_job_search(search_params: dict) -> JSONResponse | dict | ValueError:
    q = search_params.get("q", None)
    page = search_params.get("page", 20)
    page_size = search_params.get("page_size", 20)
    mode = search_params.get("mode", "semantic")

    
    if not q:
        return JSONResponse({
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        })
    vec = embedding_service.embed_texts([q])[0]

    offset = (page - 1) * page_size

    match mode:
        case "semantic":
            total = search_service.get_total_jobs_with_embeddings()
            items = search_service.search_semantic(
                vec, 
                limit=page_size,  # Changed from top_k
                offset=offset      # Pass offset!
            )
        case "hybrid":
            total = search_service.get_total_jobs_with_embeddings()
            items = search_service.search_hybrid(
                vec, 
                limit=page_size,
                offset=offset,
                q_text=q
            )
        case _:
            raise ValueError(f"Unknown search mode: {mode}")
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total ,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

def scrape_jobs() -> None:
    print("Starting scraping jobs...")
    batch = []
    if settings.ashby_orgs: batch += scraper_service.fetch_ashby(settings.ashby_orgs)
    if settings.greenhouse_boards: batch += scraper_service.fetch_greenhouse(settings.greenhouse_boards)
    n = db_insertion_service.insert_jobs_into_db(batch)
    embedding_service.embed_data()
    print(f"ingested {n} rows")

def get_job_by_id(job_id: str):
    with database_service.get_db_context() as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()

    return row


def get_statistics(top_n_companies: int = 10, days_back: int = 30):
    """Get comprehensive job statistics using CTEs."""
    
    query = text("""
        WITH active_jobs AS (
            SELECT
                id,
                (posted_at)::date AS posting_date,
                locations,
                company,
                title
            FROM jobs
            WHERE posted_at >= now() - interval ':days_back days'
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
            LIMIT :top_n
        ),
        stats_summary AS (
            SELECT 
                COUNT(DISTINCT id) as total_active_jobs,
                COUNT(DISTINCT company) as total_active_companies,
                MAX(posting_date) as latest_job_date
            FROM active_jobs
            WHERE company IS NOT NULL AND company <> ''
        ),
        company_offer_type AS (
            SELECT 
                company,
                SUM(CASE WHEN UPPER(title) ~* 'ENGINEER|DEVELOPER|SOFTWARE|SWE|DEVOPS|DATA ENGINEER|ML ENGINEER' 
                    THEN 1 ELSE 0 END) AS engineer,
                SUM(CASE WHEN NOT (UPPER(title) ~* 'ENGINEER|DEVELOPER|SOFTWARE|SWE|DEVOPS|DATA ENGINEER|ML ENGINEER') 
                    THEN 1 ELSE 0 END) AS other,
                COUNT(*) AS total
            FROM active_jobs
            WHERE company IS NOT NULL AND company <> ''
            GROUP BY company
            ORDER BY total DESC
            LIMIT :top_n
        )
        SELECT 
            (SELECT jsonb_agg(jpd ORDER BY jpd.date) FROM jobs_per_day jpd) AS jobs_per_day,
            (SELECT jsonb_agg(jpc ORDER BY jpc.count DESC) FROM jobs_per_country jpc) AS jobs_per_country,
            (SELECT jsonb_agg(tc) FROM top_companies tc) AS top_companies,
            (SELECT jsonb_agg(cot) FROM company_offer_type cot) AS company_offer_type,
            (SELECT row_to_json(ss) FROM stats_summary ss) AS stats_summary
    """)
    
    with database_service.get_db_context() as db:
        result = db.execute(query, {
            "days_back": days_back,
            "top_n": top_n_companies
        })
        row = result.fetchone()

        stats = {
            "jobs_per_day": row.jobs_per_day or [],
            "top_companies": row.top_companies or [],
            "company_offer_type": row.company_offer_type or [],
            "stats_summary": row.stats_summary or {}
        }
        
        formatted_countries = []
        if row.jobs_per_country:
            formatted_countries = format_jobs_per_country(row.jobs_per_country)

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