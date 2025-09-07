-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS citext;

-- Core jobs
CREATE TABLE IF NOT EXISTS jobs (
  id               TEXT PRIMARY KEY,
  source           TEXT NOT NULL,
  source_id        TEXT,
  company          CITEXT NOT NULL,
  title            TEXT  NOT NULL,
  locations        JSONB NOT NULL DEFAULT '[]',
  remote           BOOLEAN,
  posted_at        TIMESTAMPTZ,
  url              TEXT,
  description_html TEXT,
  description_text TEXT,
  tags             TEXT[] DEFAULT '{}',
  compensation     JSONB,
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  inserted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Embeddings
CREATE TABLE IF NOT EXISTS job_embeddings (
  job_id      TEXT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
  model_name  TEXT NOT NULL,
  embedding   VECTOR(384) NOT NULL,
  embedded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS job_embeddings_ivfflat_cos
  ON job_embeddings USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX IF NOT EXISTS jobs_posted_at_idx ON jobs (posted_at DESC);
CREATE INDEX IF NOT EXISTS jobs_company_idx   ON jobs (company);
