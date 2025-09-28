from __future__ import annotations
import re, html
from sentence_transformers import SentenceTransformer
from src.settings import settings
from src.database import database_service
from psycopg2.extras import execute_values
from src.services.embedding.embedding_sql import _SQL_SELECT_MISSING_EMBEDDINGS, _SQL_UPSERT_EMBEDDINGS

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_model: SentenceTransformer | None = None


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return html.unescape(text).strip()

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.model.MODEL_NAME)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vecs = model.encode(texts, batch_size=settings.model.BATCH_SIZE, normalize_embeddings=True)
    return [v.tolist() for v in vecs]


def fetch_missing_embeddings(limit: int = 512) -> list[tuple[str, str]]:
    with database_service.get_cursor() as cur:
        # The new SQL query expects one parameter for the LIMIT clause
        cur.execute(_SQL_SELECT_MISSING_EMBEDDINGS, (limit,))
        rows = cur.fetchall()
    
    # The return statement must match the columns from the new SQL query: 'id' and 'text_to_embed'
    return [(r["id"], r['text_to_embed']) for r in rows]


def insert_embeddings(pairs: list[tuple[str, list[float]]]) -> int:
    if not pairs:
        return 0

    data_to_insert = [
            (
                job_id,
                settings.model.MODEL_NAME,
                embedding # This is the key change
            )
            for job_id, embedding in pairs
        ]

    with database_service.get_cursor() as cur:
        execute_values(cur, _SQL_UPSERT_EMBEDDINGS, data_to_insert)
        return cur.rowcount
    
def embed_data():
    total = 0
    while True:
        todo = fetch_missing_embeddings(limit=settings.model.BATCH_SIZE * 4)
        if not todo: break
        ids, texts = zip(*todo)
        vecs = embed_texts(list(texts))
        total += insert_embeddings(list(zip(ids, vecs)))
    print(f"embedded {total} rows")