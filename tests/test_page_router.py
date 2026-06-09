from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.page import Page


def test_health_check_endpoint(client: TestClient):
    """Test that the system health endpoint returns a healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


from unittest.mock import MagicMock

def test_get_page_api_flow(client: TestClient, db_session: Session):
    """Test the HTTP flow of scraping, saving, and querying pages via API routes."""
    # Mock the page service's scraper to avoid actual network calls
    from app.routers.page_router import page_service
    mock_payload = {
        "page": {
            "page_id": "deepsolv",
            "name": "Deepsolv",
            "follower_count": 4200
        },
        "posts": [
            {
                "content": "Exciting post about AI",
                "likes_count": 10,
                "comments": [{"author_name": "Bob", "text": "Wow"}]
            }
        ],
        "employees": [
            {"name": "Developer Joe", "title": "Developer"}
        ]
    }
    page_service.scraper.scrape_all = MagicMock(return_value=mock_payload)

    # Retrieve details for a page not in database (forces mock-scraping)
    response = client.get("/api/v1/pages/deepsolv")
    assert response.status_code == 200
    data = response.json()
    
    assert data["page_id"] == "deepsolv"
    assert "Deepsolv" in data["name"]
    assert len(data["recent_posts"]) > 0
    assert len(data["recent_employees"]) > 0

    # Retrieve again (should match cache and return from database)
    cached_response = client.get("/api/v1/pages/deepsolv")
    assert cached_response.status_code == 200
    assert cached_response.json()["id"] == data["id"]


def test_get_pages_paginated_list_endpoint(client: TestClient, db_session: Session):
    """Test pagination structures and filtering query parameters on the pages listing endpoint."""
    # Seed 3 pages to query
    db_session.add(Page(page_id="p1", name="Product A", industry="Tech", follower_count=100))
    db_session.add(Page(page_id="p2", name="Product B", industry="Finance", follower_count=200))
    db_session.add(Page(page_id="p3", name="Product C", industry="Tech", follower_count=300))
    db_session.commit()

    # Query with filtering and pagination
    response = client.get("/api/v1/pages?industry=Tech&page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["total_pages"] == 1
    assert len(data["results"]) == 2
    assert data["results"][0]["page_id"] in ["p1", "p3"]


def test_get_comments_endpoint(client: TestClient, db_session: Session):
    """Test retrieving comments for a post via the API."""
    # Mock the scraper
    from app.routers.page_router import page_service
    mock_payload = {
        "page": {
            "page_id": "deepsolv",
            "name": "Deepsolv",
            "follower_count": 4200
        },
        "posts": [
            {
                "content": "Exciting post about AI",
                "likes_count": 10,
                "comments": [{"author_name": "Bob", "text": "Wow"}]
            }
        ],
        "employees": [
            {"name": "Developer Joe", "title": "Developer"}
        ]
    }
    page_service.scraper.scrape_all = MagicMock(return_value=mock_payload)

    # Scrape to populate database
    response = client.get("/api/v1/pages/deepsolv")
    assert response.status_code == 200
    page_data = response.json()
    
    # Get posts of the page
    posts_response = client.get("/api/v1/pages/deepsolv/posts?page=1&size=5")
    assert posts_response.status_code == 200
    posts_data = posts_response.json()
    assert len(posts_data["results"]) > 0
    post_id = posts_data["results"][0]["id"]
    
    # Retrieve comments
    comments_response = client.get(f"/api/v1/pages/deepsolv/posts/{post_id}/comments?page=1&size=5")
    assert comments_response.status_code == 200
    comments_data = comments_response.json()
    assert "results" in comments_data
    assert "total" in comments_data

