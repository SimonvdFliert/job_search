from fastapi import APIRouter, Depends
from src.auth import deps as auth_deps
from src.scrapers import scraper_service

router = APIRouter(prefix="/data", tags=["scraper"])

@router.get('/external_retrieval')
def scraper_data(admin = Depends(auth_deps.require_admin)):
    scraper_service.scrape_jobs()