INSERT INTO jobs (
  id, source, source_id, company, title, locations, remote, posted_at, url,
  description_html, description_text, tags, compensation, is_active, updated_at
) VALUES %s
ON CONFLICT (id) DO UPDATE SET
  source = EXCLUDED.source,
  source_id = EXCLUDED.source_id,
  company = EXCLUDED.company,
  title = EXCLUDED.title,
  locations = EXCLUDED.locations,
  remote = EXCLUDED.remote,
  posted_at = EXCLUDED.posted_at,
  url = EXCLUDED.url,
  description_html = EXCLUDED.description_html,
  description_text = EXCLUDED.description_text,
  tags = EXCLUDED.tags,
  compensation = EXCLUDED.compensation,
  is_active = TRUE,
  updated_at = now();
