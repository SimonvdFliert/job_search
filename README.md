TODO:
1. webscraper career page
2. Get links to interesting jobs based on title
3. Scrape those links
4. Put data in db


# Purpose
Job search toy app for practicing gcp + deployment

# Scope
Data: OpenAI and Anthropic Job positions run manually through admin endpoint

Tech stack: Nuxt frontend, fastapi backend, embedded data for vector search

# Out of scope
LLM chat


# Running postgres
docker compose up

# execing into the db
// docker exec -it <container_name> psql -U <user> -d <db_name>
docker exec -it job_search-db-1 psql -U route_admin -d jobsdb

-- Check installed extensions
\dx

-- Check table creation
\dt

-- Check table structure
\d items
