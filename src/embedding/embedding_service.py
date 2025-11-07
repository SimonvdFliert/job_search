from __future__ import annotations
import re, html
from sentence_transformers import SentenceTransformer
from src.settings import settings
from src.database import database_service
from src.embedding.embedding_sql import _SQL_SELECT_MISSING_EMBEDDINGS, _SQL_UPSERT_EMBEDDINGS
from sqlalchemy import text

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
        _model = SentenceTransformer(settings.model_name)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vecs = model.encode(texts, batch_size=settings.model_batch_size, normalize_embeddings=True)
    return [v.tolist() for v in vecs]


def fetch_missing_embeddings() -> list[tuple[str, str]]:
    with database_service.get_db_context() as db:
        result = db.execute(text(_SQL_SELECT_MISSING_EMBEDDINGS))
        rows = result.mappings().all()
        print('fetched missing embeddings:', len(rows))
    return [(r["id"], r['text_to_embed']) for r in rows]


def insert_embeddings(pairs: list[tuple[str, list[float]]]) -> int:
    if not pairs:
        return 0

    data_to_insert = [
            {
                'job_id': job_id,
                'model_name': settings.model_name,
                'embedding': embedding
            }
            for job_id, embedding in pairs
        ]

    with database_service.get_db_context() as db:
        try:
            result = db.execute(text(_SQL_UPSERT_EMBEDDINGS), data_to_insert)
            db.commit()
            return result.rowcount
        except Exception as e:
            db.rollback()
            raise e
    
def embed_data():
    total = 0
    while True:
        todo = fetch_missing_embeddings()
        if not todo: break
        ids, texts = zip(*todo)
        vecs = embed_texts(list(texts))
        total += insert_embeddings(list(zip(ids, vecs)))
    print(f"embedded {total} rows")