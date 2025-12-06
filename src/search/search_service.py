from src.database import database_service
from sqlalchemy import text
from src.database.models import Job, JobEmbedding
from sqlalchemy import and_, case
from fastapi.responses import JSONResponse
from src.embedding import embedding_service

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
            total = get_total_jobs_with_embeddings()
            items = search_semantic(
                vec, 
                limit=page_size,
                offset=offset
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


def get_total_jobs_with_embeddings() -> int:
    """Get total count of all active jobs that have embeddings"""
    with database_service.get_db_context() as db:
        total_query = text("""
            SELECT COUNT(DISTINCT j.id)
            FROM jobs j
            INNER JOIN job_embeddings je ON j.id = je.job_id
            WHERE j.is_active = TRUE
        """)
        total_result = db.execute(total_query)
        total = total_result.scalar()
    return total


def search_semantic(
    q_embed: list[float],
    limit: int = 20,
    offset: int = 0,
    company: str | None = None,
    q_loc: str | None = None
):
    
    with database_service.get_db_context() as db:
        db.execute(text("SET LOCAL ivfflat.probes = 10"))
        
        cosine_sim = (1 - JobEmbedding.embedding.cosine_distance(q_embed)).label("cosine_sim")
        
        query = db.query(
            Job,
            cosine_sim
                ).join(
                    JobEmbedding, Job.id == JobEmbedding.job_id
                ).filter(
                    and_(
                        Job.is_active == True,
                    )
                )

        results = query.order_by(
            cosine_sim.desc(),
            Job.posted_at.desc().nullslast()
        ).limit(limit).offset(offset).all()

        return [
            {
                "id": job.id,
                "company": job.company,
                "title": job.title,
                "locations": job.locations,
                "url": job.url,
                "posted_at": job.posted_at,
                "cosine_sim": float(sim)
            }
            for job, sim in results
        ]
