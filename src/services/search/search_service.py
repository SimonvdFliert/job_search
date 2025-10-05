from src.database import database_service
from src.settings import settings
from src.services.search.search_sql import SQL_SEARCH_SEMANTIC, SQL_SEARCH_HYBRID
from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, text

def _array_literal(vec: list[float]) -> str:
    return "{" + ",".join(f"{x:.6f}" for x in vec) + "}"

def search_semantic(q_embed: list[float],
                    top_k: int = 20,
                    company: str | None = None,
                    q_loc: str | None = None):
 
    # embedding_param = cast(text(':embedding'), Vector(386))  # adjust dimension

    with database_service.get_db_context() as db:
        result = db.execute(SQL_SEARCH_SEMANTIC, {
            "embedding": q_embed,  # ← This was missing!
            "company": company,
            "location": q_loc,
            "limit": top_k
        })
        return result.fetchall()

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
