from __future__ import annotations
import re, html
from typing import List
from sentence_transformers import SentenceTransformer
from .settings import settings

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

def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_model()
    vecs = model.encode(texts, batch_size=settings.model.BATCH_SIZE, normalize_embeddings=True)
    return [v.tolist() for v in vecs]
