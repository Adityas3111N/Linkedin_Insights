# LinkedIn Insights Microservice

## Project Overview
A backend microservice that scrapes LinkedIn company pages, stores structured data in MySQL, and exposes RESTful APIs with filtering and pagination. Built for the Deepsolv SDE Intern assignment.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MySQL 8.x via SQLAlchemy 2.0 ORM
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (for scraping)
- **HTML Parsing**: BeautifulSoup4
- **Testing**: pytest
- **Server**: uvicorn

## Architecture — Repository + Service Pattern

```
Request → Router → Service → Repository → MySQL
                     ↓
                  Scraper (only when data is missing from DB)
```

### Layer Rules (STRICTLY FOLLOW THESE)
1. **Routers** (`app/routers/`) — Handle HTTP only. No business logic. No direct DB queries. Call service methods, return responses.
2. **Services** (`app/services/`) — Business logic and orchestration. Call repositories for DB access. Call scraper for LinkedIn data. Raise domain exceptions (never HTTP exceptions).
3. **Repositories** (`app/repositories/`) — Database queries only. Accept a `Session` parameter. Return SQLAlchemy model instances. No business logic.
4. **Models** (`app/models/`) — SQLAlchemy ORM table definitions. One file per table. All models inherit from `Base` in `base.py`.
5. **Schemas** (`app/schemas/`) — Pydantic models for request/response validation. Separate from ORM models. Never expose internal IDs or raw timestamps without formatting.
6. **Utils** (`app/utils/`) — Shared helpers, custom exceptions, pagination logic.

### Dependency Flow (one-way only)
```
routers → services → repositories → models
                  → scraper_service
schemas are used by routers and services
utils are used by anyone
```
**NEVER** import routers from services, or services from repositories. Dependencies flow ONE direction only.

## Database Conventions
- **Primary keys**: Auto-increment integer `id` on every table.
- **Natural keys**: `page_id` (the LinkedIn slug) is a UNIQUE string column, used for API lookups.
- **Timestamps**: Every table has `created_at` with `server_default=func.now()`. The `pages` table also has `updated_at`.
- **Foreign keys**: Always use `ondelete="CASCADE"`. Deleting a page removes all its posts, comments, and employees.
- **Indexes**: Add indexes on columns used in WHERE clauses — `follower_count`, `industry`, `name`.
- **JSON columns**: Use MySQL JSON type for simple lists (like `specialities`). Do not create junction tables for simple string arrays.

## Naming Conventions
- **Files**: lowercase with underscores — `page_repository.py`, `scraper_service.py`
- **Classes**: PascalCase — `PageRepository`, `ScraperService`, `PageResponse`
- **Functions**: snake_case — `find_by_page_id()`, `scrape_page()`
- **Database tables**: lowercase plural — `pages`, `posts`, `comments`, `employees`
- **API routes**: lowercase with hyphens — `/api/v1/pages/{page_id}/posts`
- **Constants**: UPPER_SNAKE_CASE — `DEFAULT_PAGE_SIZE = 10`

## API Design Rules
- All endpoints are prefixed with `/api/v1/`
- Use plural nouns for resources: `/pages`, `/posts` (not `/page`, `/post`)
- Nested resources for relationships: `/pages/{page_id}/posts`, `/posts/{post_id}/comments`
- Pagination via query params: `?page=1&size=10` (defaults: page=1, size=10, max size=50)
- Filtering via query params: `?industry=Technology&min_followers=10000`
- All list endpoints return a `PaginatedResponse` wrapper with `total`, `page`, `size`, `total_pages`, `results`
- All error responses follow: `{"detail": "Human-readable error message"}`

## Error Handling Pattern
- Services raise **domain exceptions** (`PageNotFoundException`, `ScrapingException`)
- `main.py` registers **global exception handlers** that map domain exceptions → HTTP status codes
- Repositories NEVER raise HTTP exceptions
- Services NEVER return HTTP responses

## Key Business Rule — Scrape-If-Missing
When a GET request comes for a `page_id` that's not in the DB:
1. Try scraping it from LinkedIn
2. If scraping succeeds → save to DB → return data
3. If scraping fails → return 404

This means the DB acts as a cache. Scrape once, serve from DB forever after.

## Testing Strategy
- Use SQLite in-memory for test database (faster than real MySQL)
- Mock the scraper in service tests (never hit LinkedIn during tests)
- Use FastAPI's `TestClient` for integration tests
- Test files mirror source structure: `test_page_repository.py`, `test_page_service.py`, `test_page_router.py`

## What NOT To Do
- Do NOT put SQL queries inside route handlers
- Do NOT use `db.execute(text("raw SQL"))` — use SQLAlchemy ORM queries
- Do NOT catch generic `Exception` — catch specific exception types
- Do NOT return SQLAlchemy model objects directly from API — convert to Pydantic schemas
- Do NOT hardcode database credentials — always use `.env` via `pydantic-settings`
- Do NOT commit the `.env` file — it's in `.gitignore`
