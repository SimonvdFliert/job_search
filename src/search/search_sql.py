# from sqlalchemy import text

# SQL_SEARCH_SEMANTIC = text("""
# SET LOCAL ivfflat.probes = 10;
# WITH base AS (
#   SELECT
#     j.id,
#     j.company,
#     j.title,
#     j.locations,
#     j.url,
#     j.posted_at,
#     (1 - (e.embedding <=> :embedding)) AS cosine_sim
#   FROM job_embeddings e
#   JOIN jobs j ON j.id = e.job_id
#   WHERE j.is_active
#     AND (:company IS NULL OR j.company = :company)
#     AND (:location IS NULL OR EXISTS (
#           SELECT 1 FROM jsonb_array_elements_text(j.locations) loc
#           WHERE loc ILIKE '%%' || :location || '%%'
#         ))
# )
# SELECT * FROM base
# ORDER BY cosine_sim DESC, posted_at DESC NULLS LAST
# LIMIT :limit;
# """)