from src.scrapers import scraper_service
import pytest
import pytest_mock

def test_strip_html():
    raw_html = "<div><h1>Job Title</h1><p>This is a <b>great</b> job.</p></div>"
    expected_output = "Job Title This is a great job."
    assert scraper_service.strip_html(raw_html) == expected_output

def test_strip_html_empty():
    raw_html = None
    expected_output = ""
    assert scraper_service.strip_html(raw_html) == expected_output


@pytest.mark.parametrize(
    "title,description,expected",
    [
        ("AI Researcher", "We work on artificial intelligence.", True),
        ("Data Scientist", "Experience with machine learning required.", True),
        ("Software Engineer", "No experience needed.", False),
        ("ML Engineer", "Join our team to build ML models.", True),
        ("Backend Developer", "Focus on server-side logic.", False),
    ],
)
def test_ai_role(title, description, expected):
    assert scraper_service.is_ai_role(title, description) is expected


