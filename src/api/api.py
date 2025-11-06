from __future__ import annotations
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends

from starlette.middleware.cors import CORSMiddleware
from typing import Any
import src.api.api_services as api_svc
from pydantic import BaseModel
from src.api.routers import auth_router
from src.api import auth_services
from starlette.middleware.sessions import SessionMiddleware
from src.settings import settings


app = FastAPI(title="Jobs API")
print('secret key', settings.secret_key)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    path="/",  # Add this
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Your Nuxt frontend
        "http://127.0.0.1:3000",      # Alternative
        "http://localhost:8000",      # Your FastAPI backend
        "http://127.0.0.1:8000",      # Alternative
        ],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router.router)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    row = api_svc.get_job_by_id(job_id)
    if not row: raise HTTPException(404, "not found")
    return row


class JobResult(BaseModel):
    id: str
    company: str
    title: str
    locations: list
    url: str
    posted_at: datetime | None
    cosine_sim: float
    # For hybrid mode:
    text_match: float | None = None
    hybrid_score: float | None = None
    
    class Config:
        # This allows Pydantic to serialize datetime objects
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class PaginatedResponse(BaseModel):
    items: list[JobResult]
    total: int
    page: int
    page_size: int
    total_pages: int


@app.get("/search", response_model=PaginatedResponse)
def search(q: str = Query(""),
           page: int = Query(1, ge=1),
           page_size: int = Query(20, ge=1, le=100),
           mode: str = Query("semantic")):
    print(f"Received search request: q='{q}', page={page}, page_size={page_size}, mode={mode}")
    
    received_data: dict[str, Any] = {"q": q, 
                                    "page": page,
                                    "page_size": page_size,
                                    "mode": mode}
    
    rows = api_svc.do_job_search(received_data)
    return rows

@app.get('/data/external_retrieval')
def scraper_data(admin = Depends(auth_services.require_admin)):
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


# @app.get("/protected")
# async def protected_route(
#     current_user: Annotated[UserResponse, Depends(auth_services.get_current_active_user)]
# ):
#     return {
#         "message": f"Hello {current_user.username}!",
#         "user": current_user
#     }

