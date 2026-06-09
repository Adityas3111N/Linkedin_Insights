# Coding Conventions & Patterns

## File Organization
- One class per file (for models, repositories, schemas)
- File name matches the primary class: `page_repository.py` → `PageRepository`
- Imports are grouped in this order, with a blank line between groups:
  1. Standard library (`os`, `datetime`, `typing`)
  2. Third-party (`fastapi`, `sqlalchemy`, `pydantic`)
  3. Local app (`app.models`, `app.schemas`, `app.utils`)

## Type Hints
Every function must have type hints on parameters and return type:
```python
# Good
def find_by_page_id(self, db: Session, page_id: str) -> Optional[Page]:

# Bad — no type hints
def find_by_page_id(self, db, page_id):
```

## Docstrings (Google Style)
All public methods need a docstring:
```python
def find_all(self, db: Session, skip: int, limit: int) -> tuple[int, list[Page]]:
    """Fetch paginated list of pages from the database.

    Args:
        db: Active database session.
        skip: Number of records to skip (for pagination offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (total_count, list_of_pages).
    """
```

## Pydantic Schema Patterns
```python
class PageResponse(BaseModel):
    """Response schema for a single page."""
    page_id: str
    name: str
    follower_count: int

    model_config = ConfigDict(from_attributes=True)
```
- Always set `from_attributes=True` so Pydantic can read from SQLAlchemy objects
- Use `Optional[str]` for nullable fields, not bare `str`
- Use `Field(default=..., description="...")` for documented defaults

## Repository Pattern
```python
class PageRepository:
    """Handles all database operations for the pages table."""

    def find_by_page_id(self, db: Session, page_id: str) -> Optional[Page]:
        """Find a single page by its LinkedIn slug."""
        statement = select(Page).where(Page.page_id == page_id)
        return db.execute(statement).scalar_one_or_none()
```
- Repositories are stateless — no instance variables
- Every method takes `db: Session` as the first parameter
- Return ORM model instances, not dictionaries

## Service Pattern
```python
class PageService:
    """Business logic for page operations."""

    def __init__(self):
        self.page_repo = PageRepository()
        self.scraper = ScraperService()

    def get_page(self, db: Session, page_id: str) -> Page:
        """Get a page by ID. Scrapes from LinkedIn if not in DB."""
        page = self.page_repo.find_by_page_id(db, page_id)
        if page:
            return page

        scraped_data = self.scraper.scrape_page(page_id)
        if not scraped_data:
            raise PageNotFoundException(page_id)

        return self.page_repo.create(db, scraped_data)
```
- Services compose repositories and other services
- Raise domain exceptions, not HTTP exceptions
- Each method handles one business operation

## Router Pattern
```python
@router.get("/{page_id}", response_model=PageDetailResponse)
def get_page(page_id: str, db: Session = Depends(get_db)):
    """Fetch a LinkedIn page by its slug. Scrapes if not cached."""
    service = PageService()
    page = service.get_page(db, page_id)
    return page
```
- Use `response_model` to enforce output shape
- Use `Depends(get_db)` for database sessions
- Keep handlers thin — just call service and return

## Anti-Patterns to Avoid

### Don't mix layers
```python
# BAD — database query inside a router
@router.get("/pages/{page_id}")
def get_page(page_id: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.page_id == page_id).first()
    return page

# GOOD — router calls service, service calls repository
@router.get("/pages/{page_id}")
def get_page(page_id: str, db: Session = Depends(get_db)):
    service = PageService()
    return service.get_page(db, page_id)
```

### Don't use raw SQL
```python
# BAD
db.execute(text("SELECT * FROM pages WHERE industry = :ind"), {"ind": industry})

# GOOD
select(Page).where(Page.industry == industry)
```

### Don't catch and silence exceptions
```python
# BAD — hides bugs
try:
    page = service.get_page(db, page_id)
except Exception:
    return None

# GOOD — let domain exceptions propagate
page = service.get_page(db, page_id)  # raises PageNotFoundException if missing
```

### Don't return ORM objects from API
```python
# BAD — leaks internal fields, lazy-loading issues
@router.get("/pages/{page_id}")
def get_page(page_id: str, db = Depends(get_db)):
    return db.query(Page).first()

# GOOD — convert to Pydantic schema
@router.get("/pages/{page_id}", response_model=PageResponse)
def get_page(page_id: str, db = Depends(get_db)):
    service = PageService()
    return service.get_page(db, page_id)
```
