# LinkedIn Insights Microservice — API Testing Guide

This guide describes all available API endpoints, query parameters, copy-pasteable `curl` commands, and expected JSON structures.

---

## Quick Copy-Paste Examples (For Browser or Postman)

Here are direct URLs you can paste into your browser address bar or Postman when the server is running on `http://127.0.0.1:8000`:

*   **System Health Check**:
    `http://127.0.0.1:8000/health`
*   **Get/Scrape Deepsolv Page**:
    `http://127.0.0.1:8000/api/v1/pages/deepsolv`
*   **Get/Scrape boAt Lifestyle Page**:
    `http://127.0.0.1:8000/api/v1/pages/boAt%20Lifestyle`
*   **List Stored Pages (No filters)**:
    `http://127.0.0.1:8000/api/v1/pages`
*   **Filter Pages (Min 10k Followers)**:
    `http://127.0.0.1:8000/api/v1/pages?min_followers=10000`
*   **Filter Pages (Search for "boat" in name)**:
    `http://127.0.0.1:8000/api/v1/pages?name=boat`
*   **Get Posts for Deepsolv (Paginated - Page 1, Size 3)**:
    `http://127.0.0.1:8000/api/v1/pages/deepsolv/posts?page=1&size=3`
*   **Get Employees for boAt Lifestyle (Paginated - Page 1, Size 5)**:
    `http://127.0.0.1:8000/api/v1/pages/boAt%20Lifestyle/employees?page=1&size=5`

---

## 1. System Health
Verify the FastAPI application is alive and has successfully authenticated with your MySQL instance.

### `GET /health`
*   **Purpose**: Infrastructure monitoring, uptime, and database connection checks.
*   **Query Parameters**: None

#### Example Request
```bash
curl -X GET http://127.0.0.1:8000/health
```

#### Expected Response (`200 OK`)
```json
{
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
}
```

---

## 2. Retrieve Page Details (Scrape-If-Missing)
This is the core business logic endpoint. If you query a `page_id` (the URL slug, e.g. `deepsolv`, `boat-lifestyle`) that does not exist in your local database, it will automatically crawl the page in real-time, write all related rows (posts, comments, employees) into MySQL, and return the populated profile.

### `GET /api/v1/pages/{page_id}`
*   **Purpose**: Get complete details of a company including recent posts and employees.
*   **Path Parameters**:
    *   `page_id` (string): The slug of the company page (e.g. `deepsolv`, `boAt Lifestyle`).

#### Example Request
```bash
curl -X GET http://127.0.0.1:8000/api/v1/pages/boAt%20Lifestyle
```

#### Expected Response (`200 OK`)
Returns the complete nested company page dataset including database primary keys (`id`), timestamps (`created_at`, `updated_at`), up to 10 recent posts, and up to 10 employees.

---

## 3. List & Filter Company Pages (Paginated)
Retrieve a list of all company pages stored in your database. You can filter the results by follower count ranges, industry, or name matching.

### `GET /api/v1/pages`
*   **Purpose**: Retrieve cached profiles with advanced filtering.
*   **Query Parameters**:
    *   `page` (int, default: `1`): Page number (1-indexed).
    *   `size` (int, default: `10`, max: `50`): Number of records per page.
    *   `name` (string, optional): Case-insensitive partial name match (e.g., `boat`).
    *   `industry` (string, optional): Filter by exact industry match.
    *   `min_followers` (int, optional): Minimum follower count range filter.
    *   `max_followers` (int, optional): Maximum follower count range filter.

#### Example Request (Get pages in Tech with more than 10k followers)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/pages?industry=Technology&min_followers=10000&page=1&size=5"
```

#### Expected Response (`200 OK`)
Returns a generic paginated response structure containing the paging metadata and the results list:
```json
{
    "total": 1,
    "page": 1,
    "size": 5,
    "total_pages": 1,
    "results": [
        {
            "page_id": "deepsolv",
            "name": "Deepsolv(Creative Intelligence)",
            "url": "https://www.linkedin.com/company/deepsolv/",
            "linkedin_id": "77789060",
            "profile_pic_url": null,
            "description": "Official LinkedIn page of Deepsolv. Headquartered on LinkedIn.",
            "website": "https://www.deepsolv.com",
            "industry": "Technology, Information and Internet",
            "follower_count": 34763,
            "head_count": 185,
            "specialities": ["Software Engineering", "Product Innovation"],
            "founded": "2014",
            "id": 1,
            "created_at": "2026-06-09T11:35:22",
            "updated_at": "2026-06-09T11:35:22"
        }
    ]
}
```

---

## 4. Forced Refresh / Re-Scrape Page
Manually force a real-time scraping run of a company page. If the page already exists, it clears old records in your MySQL database (cascading to posts and employees) and re-saves fresh data.

### `POST /api/v1/pages/{page_id}/scrape`
*   **Purpose**: Update database cache with fresh data.
*   **Path Parameters**:
    *   `page_id` (string): The slug of the page to refresh.

#### Example Request
```bash
curl -X POST http://127.0.0.1:8000/api/v1/pages/deepsolv/scrape
```

#### Expected Response (`201 Created`)
Returns the freshly scraped, updated `PageDetailResponse` dataset.

---

## 5. Get Paginated Posts for a Page
Retrieve only the posts belonging to a specific company page with clean pagination.

### `GET /api/v1/pages/{page_id}/posts`
*   **Purpose**: Fetch historical posts.
*   **Path Parameters**:
    *   `page_id` (string): The slug of the page.
*   **Query Parameters**:
    *   `page` (int, default: `1`): Page number.
    *   `size` (int, default: `10`, max: `25`): Items per page.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/pages/deepsolv/posts?page=1&size=2"
```

---

## 6. Get Paginated Employees for a Page
Retrieve only the employee list belonging to a specific company page with clean pagination.

### `GET /api/v1/pages/{page_id}/employees`
*   **Purpose**: Fetch historical employee lists.
*   **Path Parameters**:
    *   `page_id` (string): The slug of the page.
*   **Query Parameters**:
    *   `page` (int, default: `1`): Page number.
    *   `size` (int, default: `10`, max: `50`): Items per page.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/pages/deepsolv/employees?page=1&size=3"
```

---

## Testing in Postman

To import these endpoints into Postman:
1. Click **Import** in Postman.
2. Select the **Raw text** option.
3. Paste the following URL to import the OpenAPI schemas directly from your running app:
   `http://127.0.0.1:8000/openapi.json`
4. Postman will automatically generate a complete request collection with all parameters and structures built for you!
