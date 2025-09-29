_SQL_SELECT_MISSING_EMBEDDINGS = """
SELECT
j.id,
j.title || ' at ' || j.company || ' in ' || COALESCE(locations_str, 'Remote') AS text_to_embed
FROM
jobs j
LEFT JOIN
job_embeddings e ON j.id = e.job_id
CROSS JOIN LATERAL (
SELECT string_agg(value, ', ')
FROM jsonb_array_elements_text(j.locations)
) AS locs(locations_str)
WHERE
e.job_id IS NULL
"""

_SQL_UPSERT_EMBEDDINGS = """
INSERT INTO job_embeddings (job_id, model_name, embedding)
VALUES %s
ON CONFLICT (job_id) DO UPDATE SET
  model_name = EXCLUDED.model_name,
  embedding  = EXCLUDED.embedding,
  embedded_at= now();
"""