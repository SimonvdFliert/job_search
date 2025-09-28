from src.database import database_service
from src.settings import settings
from src.services.search.search_sql import SQL_SEARCH_SEMANTIC, SQL_SEARCH_HYBRID

def _array_literal(vec: list[float]) -> str:
    return "{" + ",".join(f"{x:.6f}" for x in vec) + "}"

def search_semantic(q_embed: list[float],
                    top_k: int = 20,
                    company: str | None = None,
                    q_loc: str | None = None):
    params = (
        str(q_embed),
        company, company,
        q_loc, q_loc,
        top_k,
    )
    
    with database_service.get_cursor() as cur:
        cur.execute(SQL_SEARCH_SEMANTIC, params)
        return cur.fetchall()

def search_hybrid(q_embed: list[float], q_text: str, top_k: int = 20):
    params = (
        f"{_array_literal(q_embed)}::vector({settings.model.EMBED_DIM})",
        f"{_array_literal(q_embed)}::vector({settings.model.EMBED_DIM})",
        q_text,
        settings.model.RECENCY_HALF_LIFE_DAYS,
        settings.model.HYBRID_VEC_W,
        settings.model.HYBRID_KW_W,
        settings.model.HYBRID_REC_W,
        top_k,
    )
    with database_service.get_cursor() as cur:
        cur.execute(SQL_SEARCH_HYBRID, params)
        return cur.fetchall()
