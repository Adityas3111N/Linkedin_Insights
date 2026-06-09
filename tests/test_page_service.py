from unittest.mock import MagicMock
from sqlalchemy.orm import Session
import pytest

from app.services.page_service import PageService
from app.utils.exceptions import PageNotFoundException


def test_get_page_details_cache_hit(db_session: Session):
    """Test that page details are returned directly from the database if they exist (cache hit)."""
    service = PageService()
    
    # 1. Manually add page to DB
    service.page_repo.create(db_session, {
        "page_id": "test-cache",
        "name": "Cached Corp",
        "follower_count": 1200
    })
    
    # Mock the scraper so we can verify it was NEVER called
    service.scraper = MagicMock()
    
    # 2. Retrieve details
    page = service.get_page_details(db_session, "test-cache")
    
    # 3. Assert
    assert page.name == "Cached Corp"
    service.scraper.scrape_all.assert_not_called()


def test_get_page_details_cache_miss_and_scrape(db_session: Session):
    """Test that a cache miss successfully triggers the scraper and persists the data."""
    service = PageService()
    
    # Mock scraper return data
    scraped_payload = {
        "page": {
            "page_id": "new-scraped",
            "name": "Scraped Corp",
            "follower_count": 9800
        },
        "posts": [
            {
                "content": "First scraped post!",
                "likes_count": 50,
                "comments": [
                    {"author_name": "Commenter A", "text": "Great post!"}
                ]
            }
        ],
        "employees": [
            {"name": "Alice Developer", "title": "Developer"}
        ]
    }
    
    service.scraper.scrape_all = MagicMock(return_value=scraped_payload)
    
    # Fetch page details (will trigger cache miss)
    page = service.get_page_details(db_session, "new-scraped")
    
    # Assertions
    assert page.name == "Scraped Corp"
    assert len(page.posts) == 1
    assert page.posts[0].content == "First scraped post!"
    assert len(page.posts[0].comments) == 1
    assert page.posts[0].comments[0].author_name == "Commenter A"
    assert len(page.employees) == 1
    assert page.employees[0].name == "Alice Developer"
    
    # Verify it was indeed written to database
    db_page = service.page_repo.find_by_page_id(db_session, "new-scraped")
    assert db_page is not None
    assert db_page.name == "Scraped Corp"
