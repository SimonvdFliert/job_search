SET LOCAL ivfflat.probes = 10;
WITH vec AS (
  SELECT j.id, (1 - (e.embedding <=> %s)) AS sim
  FROM job_embeddings e
  JOIN jobs j ON j.id = e.job_id
  WHERE j.is_active
  ORDER BY e.embedding <=> %s
  LIMIT 300
),
kw AS (
  SELECT id,
         ts_rank_cd(
           to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description_text,'')),
           plainto_tsquery('english', %s)
         ) AS kw_score
  FROM jobs
),
rec AS (
  SELECT id,
     EXP( -LN(2) * EXTRACT(EPOCH FROM (now() - posted_at)) / (%s*24*3600) ) AS recency
  FROM jobs
)
SELECT j.id, j.company, j.title, j.locations, j.url, j.posted_at,
       v.sim, COALESCE(k.kw_score,0) AS kw_score, COALESCE(r.recency,0.5) AS recency,
       (%s * v.sim + %s * COALESCE(k.kw_score,0) + %s * COALESCE(r.recency,0)) AS score
FROM vec v
JOIN jobs j ON j.id = v.id
LEFT JOIN kw k ON k.id = j.id
LEFT JOIN rec r ON r.id = j.id
WHERE j.is_active
ORDER BY score DESC
LIMIT %s;
