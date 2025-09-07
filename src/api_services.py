from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from psycopg2.extras import Json, execute_values
from .modules.database import get_cursor
from .modules.settings import settings
from .modules.embeddings import strip_html
from .modules.sql_loader import load_sql


def _array_literal(vec: List[float]) -> str:
    return "{" + ",".join(f"{x:.6f}" for x in vec) + "}"

def _dedupe_key(company: str, title: str, loc: Optional[str], url: Optional[str]) -> str:
    import hashlib
    base = f"{(company or '').strip().lower()}|{(title or '').strip().lower()}|{(loc or '').strip().lower()}|{(url or '').strip().lower()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()

# ---------- UPSERT JOBS ----------
_UPSERT_JOBS = load_sql("upsert_jobs.sql")

def upsert_jobs(rows: List[Dict[str, Any]]) -> int:
    values = []
    for r in rows:
        company = r.get("company") or ""
        title = r.get("title") or ""
        loc = (r.get("locations") or [None])[0]
        url = r.get("url")
        jid = r.get("id") or _dedupe_key(company, title, loc, url)
        desc_html = r.get("description_html") or ""
        desc_text = r.get("description_text") or strip_html(desc_html)

        values.append((
            jid,                         # 1 id
            r.get("source"),             # 2 source
            r.get("source_id"),          # 3 source_id
            company,                     # 4 company
            title,                       # 5 title
            Json(r.get("locations") or []),  # 6 locations (jsonb)
            r.get("remote"),             # 7 remote
            r.get("posted_at"),          # 8 posted_at (ts)
            url,                         # 9 url
            desc_html,                   # 10 description_html
            desc_text,                   # 11 description_text
            r.get("tags") or [],         # 12 tags (text[])
            Json(r.get("compensation")) if r.get("compensation") is not None else None,  # 13 compensation (jsonb)
        ))
    if not values:
        return 0
    with get_cursor() as cur:
        execute_values(cur, _UPSERT_JOBS, values)
    return len(values)

# ---------- EMBEDDINGS ----------
_SELECT_MISSING = load_sql("select_missing_embeddings.sql")
_UPSERT_EMB = load_sql("upsert_embeddings.sql")

def fetch_missing_embeddings(limit: int = 512) -> List[Tuple[str, str]]:
    with get_cursor() as cur:
        cur.execute(_SELECT_MISSING, (limit,))
        rows = cur.fetchall()
    return [(r["id"], r["description_text"]) for r in rows]

def upsert_embeddings(pairs: List[Tuple[str, List[float]]]) -> int:
    if not pairs:
        return 0
    template = "(%s, %s, %s)"
    values = [(job_id, settings.model.MODEL_NAME, f"{_array_literal(vec)}::vector({settings.model.EMBED_DIM})") for job_id, vec in pairs]
    with get_cursor() as cur:
        execute_values(cur, _UPSERT_EMB, values, template=template)
    return len(values)

# ---------- SEARCH ----------
_SEARCH_SEMANTIC = load_sql("search_semantic.sql")
_SEARCH_HYBRID = load_sql("search_hybrid.sql")

def search_semantic(q_embed: List[float], top_k: int = 20, company: Optional[str] = None, q_loc: Optional[str] = None):
    params = (
        f"{_array_literal(q_embed)}::vector({settings.model.EMBED_DIM})",
        company, company,
        q_loc, q_loc,
        top_k,
    )
    with get_cursor() as cur:
        cur.execute(_SEARCH_SEMANTIC, params)
        return cur.fetchall()

def search_hybrid(q_embed: List[float], q_text: str, top_k: int = 20):
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
    with get_cursor() as cur:
        cur.execute(_SEARCH_HYBRID, params)
        return cur.fetchall()
