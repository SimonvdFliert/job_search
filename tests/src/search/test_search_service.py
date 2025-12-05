import pytest
from datetime import datetime
from sqlalchemy import text
from src.database.models import Job, JobEmbedding
from src.search.search_service import get_total_jobs_with_embeddings, search_semantic, do_job_search

# Helper to create dummy vectors of the correct size (e.g., 1536)
def create_vec(val: float, dim: int = 384):
    return [val] * dim

def test_get_total_jobs_with_embeddings(session):
    """
    Verifies that the count logic correctly filters:
    1. Only Active jobs
    2. Only jobs WITH embeddings
    """
    # 1. Active Job WITH Embedding (Should Count)
    job1 = Job(title="Python Dev",
                id="job-1-id",
                source="test-source",
                company="TestCo",
                locations={"city": "Remote"},
                remote=True, 
               is_active=True)
    session.add(job1)
    session.flush() # Flush to get the ID
    embed1 = JobEmbedding(job_id=job1.id, embedding=create_vec(0.1), model_name="test-model")
    session.add(embed1)

    # 2. Inactive Job WITH Embedding (Should NOT Count)
    job2 = Job(title="Legacy Java",
                id="job-2-id",
                source="test-source",
                company="TestCo",
                locations={"city": "Remote"},
                remote=True, 
                is_active=False)
    session.add(job2)
    session.flush()
    embed2 = JobEmbedding(job_id=job2.id, embedding=create_vec(0.1), model_name="test-model")
    session.add(embed2)

    # 3. Active Job WITHOUT Embedding (Should NOT Count)
    job3 = Job(title="New Manager",
                id="job-3-id",
                source="test-source",
                company="TestCo",
                locations={"city": "Remote"},
                remote=True,
                 is_active=True)
    session.add(job3)
    
    session.commit() # Commit to current transaction (which will be rolled back later)

    # ACTION
    count = get_total_jobs_with_embeddings()

    # ASSERT
    assert count == 1


def test_search_semantic(session):
    """
    Verifies cosine similarity sorting and field return.
    """    
    job_a = Job(
        id="job-a-id",
        source="test-source",
        locations={"city": "Remote"},
        remote=True,
        title="Perfect Match", 
        company="Tech Corp", 
        is_active=True,
        posted_at=datetime.now()
    )
    job_b = Job(
        id="job-b-id",
        source="test-source",
        locations={"city": "Remote"},
        remote=True,
        title="Bad Match", 
        company="Old Corp", 
        is_active=True,
        posted_at=datetime.now()
    )
    session.add_all([job_a, job_b])
    session.flush()

    dim_size = 384 
    query_vec = [1.0] * dim_size
    embed_a = JobEmbedding(job_id=job_a.id,
                            embedding=[1.0] * dim_size,
                            model_name="test-model")
    embed_b = JobEmbedding(job_id=job_b.id,
                            embedding=[-1.0] * dim_size,
                            model_name="test-model")
    
    session.add_all([embed_a, embed_b])
    session.commit()

    results = search_semantic(q_embed=query_vec, limit=10)

    assert len(results) == 2
    
    # 1. Verify Sort Order (Higher cosine similarity first)
    assert results[0]["id"] == job_a.id
    assert results[1]["id"] == job_b.id
    
    # 2. Verify Data Structure
    first_result = results[0]
    assert first_result["company"] == "Tech Corp"
    assert first_result["title"] == "Perfect Match"
    
    assert first_result["cosine_sim"] == pytest.approx(1.0, abs=0.001) 
    assert results[1]["cosine_sim"] == pytest.approx(-1.0, abs=0.001)

def test_do_job_search_no_query_returns_empty_response():
    """
    Test case 1: Ensures the function returns an empty JSONResponse when 'q' is missing.
    """
    search_params = {"mode": "semantic", "page": 1, "page_size": 10}
    
    # ACTION
    response = do_job_search(search_params)
    
    # ASSERT
    assert response.status_code == 200
    data = response.body.decode()
    assert '"total":0' in data
    assert '"items":[]' in data


def test_do_job_search_unknown_mode_raises_value_error():
    """
    Test case 3: Ensures that an invalid search mode raises the expected error.
    """
    search_params = {"q": "data scientist", "mode": "fuzzy"}
    
    # ACTION & ASSERT
    with pytest.raises(ValueError) as excinfo:
        do_job_search(search_params)
    
    assert "Unknown search mode: fuzzy" in str(excinfo.value)