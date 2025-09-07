SELECT j.id, j.description_text
FROM jobs j
LEFT JOIN job_embeddings e ON e.job_id = j.id
WHERE j.is_active AND e.job_id IS NULL AND j.description_text IS NOT NULL
ORDER BY j.inserted_at ASC
LIMIT %s;
