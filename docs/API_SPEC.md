# API Specification

Base URL: `http://localhost:8000/api/v1`

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/pages` | List pages (with filters + pagination) |
| GET | `/pages/{page_id}` | Get single page details |
| GET | `/pages/{page_id}/posts` | Get posts for a page |
| GET | `/pages/{page_id}/posts/{post_id}/comments` | Get comments on a post |
| GET | `/pages/{page_id}/employees` | Get employees of a page |
| POST | `/pages/{page_id}/scrape` | Force scrape/re-scrape a page |

---

## GET /health

Returns server and database connection status.

**Response** `200 OK`:
```json
{
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
}
```

---

## GET /pages

List all scraped pages with optional filters and pagination.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number (1-indexed) |
| size | int | 10 | Results per page (max 50) |
| industry | string | null | Filter by exact industry match |
| min_followers | int | null | Minimum follower count |
| max_followers | int | null | Maximum follower count |
| name | string | null | Partial name search (case-insensitive) |

**Example**: `GET /pages?industry=Technology&min_followers=10000&page=1&size=5`

**Response** `200 OK`:
```json
{
    "total": 23,
    "page": 1,
    "size": 5,
    "total_pages": 5,
    "results": [
        {
            "page_id": "deepsolv",
            "name": "Deepsolv",
            "url": "https://www.linkedin.com/company/deepsolv/",
            "profile_pic_url": "https://...",
            "industry": "Technology",
            "follower_count": 15200,
            "head_count": 45,
            "website": "https://deepsolv.com",
            "founded": "2020",
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

---

## GET /pages/{page_id}

Get full details of a single page. If the page is NOT in the database, the service will attempt to scrape it from LinkedIn first.

**Path Parameters**: `page_id` (string) — the LinkedIn URL slug

**Response** `200 OK`:
```json
{
    "page_id": "deepsolv",
    "name": "Deepsolv",
    "url": "https://www.linkedin.com/company/deepsolv/",
    "linkedin_id": "12345678",
    "profile_pic_url": "https://...",
    "description": "AI-powered solutions for...",
    "website": "https://deepsolv.com",
    "industry": "Technology",
    "follower_count": 15200,
    "head_count": 45,
    "specialities": ["AI", "Machine Learning", "SaaS"],
    "founded": "2020",
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-06-01T14:20:00",
    "recent_posts": [
        {
            "id": 1,
            "content": "Excited to announce...",
            "likes_count": 342,
            "comments_count": 28,
            "posted_at": "2025-05-30T09:00:00"
        }
    ],
    "employee_count": 45
}
```

**Response** `404 Not Found`:
```json
{
    "detail": "Page 'nonexistent-company' not found on LinkedIn"
}
```

---

## GET /pages/{page_id}/posts

Get paginated posts for a specific page.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| size | int | 10 | Results per page (max 25) |

**Response** `200 OK`:
```json
{
    "total": 18,
    "page": 1,
    "size": 10,
    "total_pages": 2,
    "results": [
        {
            "id": 1,
            "content": "We're hiring! Looking for...",
            "post_url": "https://linkedin.com/feed/...",
            "likes_count": 342,
            "comments_count": 28,
            "shares_count": 15,
            "media_url": "https://...",
            "media_type": "image",
            "posted_at": "2025-05-30T09:00:00"
        }
    ]
}
```

---

## GET /pages/{page_id}/posts/{post_id}/comments

Get paginated comments for a specific post.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| size | int | 10 | Results per page (max 50) |

**Response** `200 OK`:
```json
{
    "total": 28,
    "page": 1,
    "size": 10,
    "total_pages": 3,
    "results": [
        {
            "id": 1,
            "author_name": "Jane Smith",
            "author_profile_url": "https://linkedin.com/in/janesmith",
            "text": "Congratulations on the launch!",
            "commented_at": "2025-05-30T12:15:00"
        }
    ]
}
```

---

## GET /pages/{page_id}/employees

Get paginated list of employees for a company page.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| size | int | 10 | Results per page (max 50) |

**Response** `200 OK`:
```json
{
    "total": 45,
    "page": 1,
    "size": 10,
    "total_pages": 5,
    "results": [
        {
            "id": 1,
            "name": "John Doe",
            "title": "Senior Software Engineer",
            "profile_url": "https://linkedin.com/in/johndoe"
        }
    ]
}
```

---

## POST /pages/{page_id}/scrape

Force a fresh scrape of the page from LinkedIn, even if it already exists in the database. Updates existing data.

**Response** `200 OK`:
```json
{
    "message": "Successfully scraped and stored data for 'deepsolv'",
    "page_id": "deepsolv"
}
```

**Response** `502 Bad Gateway`:
```json
{
    "detail": "Failed to scrape page 'deepsolv' from LinkedIn. The service may be temporarily unavailable."
}
```

---

## Error Responses

All errors follow this format:

```json
{
    "detail": "Human-readable error description"
}
```

| Status Code | When |
|-------------|------|
| 400 | Invalid query parameters |
| 404 | Page not found in DB and scraping returned nothing |
| 422 | Request validation failed (Pydantic) |
| 502 | LinkedIn scraping failed (network error, blocked, etc.) |
| 500 | Unexpected server error |

## Pagination Contract

Every list endpoint returns:

```json
{
    "total": 100,
    "page": 2,
    "size": 10,
    "total_pages": 10,
    "results": []
}
```

- `page` starts at 1 (not 0)
- `size` has a maximum limit per endpoint (10-50)
- Empty results return `total: 0` and `results: []` (not 404)
