from __future__ import annotations
from fastapi import FastAPI, HTTPException

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import src.api.api_services as api_svc
from src.auth import auth_router
from src.search import search_router
from src.scrapers import scraper_router
from src.settings import settings

app = FastAPI(title="Jobs API")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    path="/",
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(search_router.router)
app.include_router(scraper_router.router)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    row = api_svc.get_job_by_id(job_id)
    if not row: raise HTTPException(404, "not found")
    return row

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
    return api_svc.get_statistics(top_n_companies=top_n_companies)
