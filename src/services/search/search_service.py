from src.database import database_service
from src.settings import settings
from src.services.search.search_sql import SQL_SEARCH_SEMANTIC, SQL_SEARCH_HYBRID
from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, text
from src.database.models import Job, JobEmbedding
from sqlalchemy import func, and_

def _array_literal(vec: list[float]) -> str:
    return "{" + ",".join(f"{x:.6f}" for x in vec) + "}"

def search_semantic(q_embed: list[float],
                    top_k: int = 20,
                    company: str | None = None,
                    q_loc: str | None = None):
    
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
        ).limit(top_k).all()

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
def search_hybrid(q_embed: list[float], q_text: str, top_k: int = 20):
    params = (
        f"{_array_literal(q_embed)}::vector({settings.model_embeded_dim})",
        f"{_array_literal(q_embed)}::vector({settings.model_embeded_dim})",
        q_text,
        settings.model_recency_half_life_days,
        settings.model_hybrid_vec_w,
        settings.model_hybrid_kw_w,
        settings.model_hybrid_rec_w,
        top_k,
    )
    with database_service.get_db_context() as cur:
        cur.execute(SQL_SEARCH_HYBRID, params)
        return cur.fetchall()
