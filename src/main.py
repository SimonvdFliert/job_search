from __future__ import annotations
import argparse, os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

from .modules.settings import settings
from .modules.database import ensure_database_exists, apply_schema, get_cursor
from .modules.embeddings import embed_texts
from .modules import scraper
from . import api_services as svc

app = FastAPI(title="Jobs API")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/job/{job_id}")
def get_job(job_id: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()
    if not row: raise HTTPException(404, "not found")
    return row

@app.get("/search")
def search(q: str = Query(""), top_k: int = Query(20, le=100), mode: str = Query("semantic")):
    if not q:
        return JSONResponse({"results": [], "took_ms": 0})
    vec = embed_texts([q])[0]
    rows = svc.search_semantic(vec, top_k=top_k) if mode == "semantic" else svc.search_hybrid(vec, q_text=q, top_k=top_k)
    return {"results": rows}

def cmd_bootstrap():
    ensure_database_exists()
    apply_schema()
    print("bootstrap complete")

def cmd_ingest():
    batch = []
    if settings.scrape.ASHBY_ORGS: batch += scraper.fetch_ashby(settings.scrape.ASHBY_ORGS)
    if settings.scrape.GREENHOUSE_BOARDS: batch += scraper.fetch_greenhouse(settings.scrape.GREENHOUSE_BOARDS)
    n = svc.upsert_jobs(batch)
    print(f"ingested {n} rows")

def cmd_embed():
    # simple loop until no more rows
    total = 0
    while True:
        todo = svc.fetch_missing_embeddings(limit=settings.model.BATCH_SIZE * 4)
        if not todo: break
        ids, texts = zip(*todo)
        vecs = embed_texts(list(texts))
        total += svc.upsert_embeddings(list(zip(ids, vecs)))
    print(f"embedded {total} rows")

def cmd_api():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["bootstrap", "ingest", "embed", "api"])
    args = parser.parse_args()

    if args.mode == "bootstrap": cmd_bootstrap()
    elif args.mode == "ingest":  cmd_ingest()
    elif args.mode == "embed":   cmd_embed()
    elif args.mode == "api":     cmd_api()
