SELECT
  j.id,
  -- Create a high-signal string with the most important info
  j.title || ' at ' || j.company || ' in ' || COALESCE(locations_str, 'Remote') AS text_to_embed
FROM
  jobs j
LEFT JOIN
  job_embeddings e ON j.id = e.job_id
-- Helper to format the locations JSONB array into a string
CROSS JOIN LATERAL (
  SELECT string_agg(value, ', ')
  FROM jsonb_array_elements_text(j.locations)
) AS locs(locations_str)
WHERE
  e.job_id IS NULL -- Only select jobs that have not been embedded yet
LIMIT %s;