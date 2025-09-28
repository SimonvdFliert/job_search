from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from starlette.middleware.cors import CORSMiddleware
from typing import Any
import src.api.api_services as api_svc

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
    row = api_svc.get_job_by_id(job_id)
    if not row: raise HTTPException(404, "not found")
    return row

@app.get("/search")
def search(q: str = Query(""), top_k: int = Query(20, le=100), mode: str = Query("semantic")):
    received_data: dict[str, Any] = {"q": q, "top_k": top_k, "mode": mode}
    rows = api_svc.do_job_search(received_data)
    return {"results": rows}

@app.get('/data/external_retrieval')
def scraper_data():
    api_svc.scrape_jobs()

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