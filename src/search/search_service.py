from src.database import database_service
from src.settings import settings
# from src.search.search_sql import SQL_SEARCH_SEMANTIC, SQL_SEARCH_HYBRID
# from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, text
from src.database.models import Job, JobEmbedding
from sqlalchemy import func, and_, case


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
    print(f"Total jobs with embeddings: {total}")
    return total


def search_semantic(
    q_embed: list[float],
    limit: int = 20,      # Renamed from page_size
    offset: int = 0,      # Added offset parameter
    company: str | None = None,
    q_loc: str | None = None
):
    
    print(f"Searching semantic with limit={limit}, offset={offset}")
    print(f"Query embedding sample: {q_embed[:5]}... (length: {len(q_embed)})")


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

def search_hybrid(
    q_embed: list[float],
    limit: int = 20,
    offset: int = 0,      # Added offset
    q_text: str = "",
    company: str | None = None,
    q_loc: str | None = None
):
    with database_service.get_db_context() as db:
        db.execute(text("SET LOCAL ivfflat.probes = 10"))
        
        cosine_sim = (1 - JobEmbedding.embedding.cosine_distance(q_embed)).label("cosine_sim")
        
        # Text search relevance (you can adjust weights)
        text_match = case(
            (Job.title.ilike(f"%{q_text}%"), 1.0),
            (Job.company.ilike(f"%{q_text}%"), 0.8),
            else_=0.0
        ).label("text_match")
        
        # Combined score
        hybrid_score = (cosine_sim * 0.7 + text_match * 0.3).label("hybrid_score")
        
        query = db.query(
            Job,
            cosine_sim,
            text_match,
            hybrid_score
        ).join(
            JobEmbedding, Job.id == JobEmbedding.job_id
        ).filter(
            and_(
                Job.is_active == True,
            )
        )

        results = query.order_by(
            hybrid_score.desc(),
            Job.posted_at.desc().nullslast()
        ).limit(limit).offset(offset).all()  # ← Added .offset(offset)

        return [
            {
                "id": job.id,
                "company": job.company,
                "title": job.title,
                "locations": job.locations,
                "url": job.url,
                "posted_at": job.posted_at,
                "cosine_sim": float(cosine),
                "text_match": float(text),
                "hybrid_score": float(hybrid)
            }
            for job, cosine, text, hybrid in results
        ]
