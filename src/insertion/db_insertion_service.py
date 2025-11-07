from __future__ import annotations
from typing import Any
from psycopg2.extras import Json, execute_values
from src.database import database_service
from src.embedding.embedding_service import strip_html
from datetime import datetime
import hashlib
from src.insertion.insertion_sql import _SQL_INSERT_INTO_DB
from sqlalchemy import text

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

        values.append({
            'id': jid,
            'source': r.get("source"),
            'source_id': r.get("source_id"),
            'company': company,
            'title': title,
            'locations': Json(r.get("locations") or []),
            'remote': r.get("remote"),
            'posted_at': r.get("posted_at"),
            'url': url,
            'description_html': desc_html,
            'description_text': desc_text,
            'tags': r.get("tags") or [],
            'compensation': Json(r.get("compensation")) if r.get("compensation") is not None else None,
            'is_active': True,
            'updated_at': datetime.now(),
        })
    if not values:
        return 0
    with database_service.get_db_context() as db:
        try:
            # Bulk insert using executemany
            db.execute(text(_SQL_INSERT_INTO_DB), values)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e