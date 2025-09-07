-- One-time extensions
CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector
CREATE EXTENSION IF NOT EXISTS citext;   -- case-insensitive text (nice for company names)

-- Core jobs
CREATE TABLE jobs (
  id               TEXT PRIMARY KEY,            -- your stable dedupe id
  source           TEXT NOT NULL,               -- "ashby" | "greenhouse"
  source_id        TEXT,
  company          CITEXT NOT NULL,
  title            TEXT  NOT NULL,
  locations        JSONB NOT NULL DEFAULT '[]',
  remote           BOOLEAN,
  posted_at        TIMESTAMPTZ,
  url              TEXT,
  description_html TEXT,                        -- for UI detail view
  description_text TEXT,                        -- for embeddings / keyword
  tags             TEXT[] DEFAULT '{}',
  compensation     JSONB,
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  inserted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Embeddings in a separate table (easy re-embed / swap models)
CREATE TABLE job_embeddings (
  job_id      TEXT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
  model_name  TEXT NOT NULL,
  embedding   VECTOR(384) NOT NULL,             -- 384 if using MiniLM-L6-v2
  embedded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ANN index (tune lists for your scale; 100 is fine to start)
CREATE INDEX job_embeddings_ivfflat_cos
ON job_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
