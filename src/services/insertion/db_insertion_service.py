from __future__ import annotations
from typing import Any
from psycopg2.extras import Json, execute_values
from src.database import database_service
from src.services.embedding.embedding_service import strip_html
from datetime import datetime
import hashlib
from src.services.insertion.insertion_sql import _SQL_INSERT_INTO_DB

def _dedupe_key(company: str,
                title: str,
                loc: str | None,
                url: str | None) -> str:
    base = f"{(company or '').strip().lower()}|{(title or '').strip().lower()}|{(loc or '').strip().lower()}|{(url or '').strip().lower()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()

def insert_jobs_into_db(rows: list[dict[str, Any]]) -> int:
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
            jid,                         
            r.get("source"),             
            r.get("source_id"),          
            company,                     
            title,                       
            Json(r.get("locations") or []),
            r.get("remote"),             
            r.get("posted_at"),
            url,                         
            desc_html,                   
            desc_text,                   
            r.get("tags") or [],
            Json(r.get("compensation")) if r.get("compensation") is not None else None,
            True, #14 is active
            updated_at := datetime.now(),
        ))
    if not values:
        return 0
    with database_service.get_db_context() as cur:
        execute_values(cur, _SQL_INSERT_INTO_DB, values)
    return len(values)