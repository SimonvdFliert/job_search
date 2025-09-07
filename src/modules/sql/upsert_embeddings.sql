INSERT INTO job_embeddings (job_id, model_name, embedding)
VALUES %s
ON CONFLICT (job_id) DO UPDATE SET
  model_name = EXCLUDED.model_name,
  embedding  = EXCLUDED.embedding,
  embedded_at= now();
