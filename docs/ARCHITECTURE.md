# Architecture Guide

## Why This Architecture?

This project uses the **Repository Pattern** combined with a **Service Layer**. This is the same pattern used at companies like Uber, Stripe, and most production Python backends. The core idea: **each layer has exactly one job**.

## Data Flow

```
[Client / Postman]
       │
       ▼
┌──────────────┐
│   Router     │  ← Accepts HTTP request, validates input via Pydantic
│  (page_router)│  ← Calls the appropriate service method
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Service    │  ← Contains business logic
│ (page_service)│  ← Decides: check DB first, scrape if missing
│              │  ← Raises domain exceptions (not HTTP errors)
└──────┬───────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  Repository  │   │   Scraper    │
│(page_repo)   │   │(scraper_svc) │
│              │   │              │
│ DB queries   │   │ LinkedIn     │
│ only         │   │ fetching     │
└──────┬───────┘   └──────────────┘
       │
       ▼
┌──────────────┐
│   MySQL DB   │
└──────────────┘
```

## Layer Details

### Router Layer (`app/routers/`)
**Job**: Translate between HTTP and Python.

- Receives the HTTP request
- Extracts path params, query params, request body
- Calls the correct service method
- Converts service response to Pydantic schema
- Returns the HTTP response with correct status code

**Does NOT**: Query the database, scrape LinkedIn, make business decisions.

### Service Layer (`app/services/`)
**Job**: Business logic and orchestration.

- Implements the "scrape-if-missing" pattern
- Coordinates between repository and scraper
- Applies business rules (e.g., limit to 25 posts per page)
- Raises meaningful domain exceptions

**Does NOT**: Know about HTTP status codes, handle request/response formatting, run SQL.

### Repository Layer (`app/repositories/`)
**Job**: Database access only.

- Runs SQLAlchemy queries
- Handles pagination at the query level (OFFSET/LIMIT)
- Handles dynamic filtering (building WHERE clauses)
- Returns ORM model instances

**Does NOT**: Contain business logic, make decisions about what to scrape, format responses.

### Scraper Layer (`app/services/scraper_service.py`)
**Job**: Fetch data from LinkedIn.

- Makes HTTP requests to LinkedIn
- Parses HTML/JSON responses
- Returns raw dictionaries of scraped data
- Handles retry logic and rate limiting

**Does NOT**: Save to database, know about our ORM models, make business decisions.

## Why Not Just Put Everything in the Router?

Consider this scenario: "We need to add a CLI tool that also fetches LinkedIn data."

- **With this architecture**: The CLI imports `PageService` and calls `get_page()`. Done. Zero code duplication.
- **Without layers**: You'd copy-paste the DB logic, scraper logic, and error handling into the CLI. Bug in one place? Now you have to fix it in two.

## Dependency Injection

FastAPI's `Depends()` mechanism injects database sessions into route handlers:

```python
@router.get("/pages/{page_id}")
def get_page(page_id: str, db: Session = Depends(get_db)):
    service = PageService()
    return service.get_page(db, page_id)
```

The `get_db()` function:
1. Creates a new database session
2. Yields it to the handler
3. Closes it after the handler finishes (even if it crashes)

This means route handlers never manage their own DB connections.

## Error Propagation

```
Repository → may raise SQLAlchemy errors (caught by service)
Service    → raises domain exceptions (PageNotFoundException, ScrapingException)
Router     → global handlers catch domain exceptions → return HTTP errors
```

This keeps HTTP concerns out of business logic. If we ever build a GraphQL API or CLI on top of the same services, the error types still make sense.
