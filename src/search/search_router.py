from fastapi import APIRouter, Query
from typing import Any
from src.search.schemas import PaginatedResponse
from src.search import search_service

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=PaginatedResponse)
def search(q: str = Query(""),
           page: int = Query(1, ge=1),
           page_size: int = Query(20, ge=1, le=100),
           mode: str = Query("semantic")):
    
    received_data: dict[str, Any] = {"q": q, 
                                    "page": page,
                                    "page_size": page_size,
                                    "mode": mode}
    
    rows = search_service.do_job_search(received_data)
    return rows