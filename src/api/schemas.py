from pydantic import BaseModel
from datetime import datetime

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