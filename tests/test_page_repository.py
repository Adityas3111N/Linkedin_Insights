from sqlalchemy.orm import Session
from app.models.page import Page
from app.repositories.page_repository import PageRepository
from app.schemas.page import PageListFilters


def test_create_and_find_page(db_session: Session):
    """Test standard database creation and retrieval operations on the page repository."""
    repo = PageRepository()
    
    # Arrange page data
    page_data = {
        "page_id": "test-corp",
        "name": "Test Corporation",
        "url": "https://linkedin.com/company/test-corp",
        "follower_count": 5000,
        "industry": "Software",
        "specialities": ["Cloud", "AI"]
    }
    
    # Act
    created_page = repo.create(db_session, page_data)
    found_page = repo.find_by_page_id(db_session, "test-corp")
    
    # Assert
    assert created_page.id is not None
    assert found_page is not None
    assert found_page.name == "Test Corporation"
    assert found_page.follower_count == 5000
    assert found_page.specialities == ["Cloud", "AI"]


def test_find_all_with_filters(db_session: Session):
    """Test dynamic query filtering (by industry, followers, name) on the page repository."""
    repo = PageRepository()
    
    # Seed mock records
    repo.create(db_session, {"page_id": "c1", "name": "Apple", "industry": "Hardware", "follower_count": 10000})
    repo.create(db_session, {"page_id": "c2", "name": "Google", "industry": "Software", "follower_count": 25000})
    repo.create(db_session, {"page_id": "c3", "name": "Microsoft", "industry": "Software", "follower_count": 45000})
    
    # Filter by industry
    filters = PageListFilters(industry="Software")
    total, results = repo.find_all(db_session, skip=0, limit=10, filters=filters)
    assert total == 2
    assert {p.name for p in results} == {"Google", "Microsoft"}
    
    # Filter by follower ranges
    filters = PageListFilters(min_followers=20000, max_followers=30000)
    total, results = repo.find_all(db_session, skip=0, limit=10, filters=filters)
    assert total == 1
    assert results[0].name == "Google"
    
    # Partial name query match
    filters = PageListFilters(name="micro")
    total, results = repo.find_all(db_session, skip=0, limit=10, filters=filters)
    assert total == 1
    assert results[0].name == "Microsoft"
