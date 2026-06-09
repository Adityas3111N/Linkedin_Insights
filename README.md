I have added postmanCollection.json in docs folder. It was not getting uploaded in form due to server issues. 

# LinkedIn Insights Microservice

A backend microservice built with **FastAPI**, **SQLAlchemy 2.0**, and **MySQL**. It scrapes LinkedIn company details, posts, comments, and employees in real-time, caches data into a structured relational database, and exposes clean RESTful APIs with advanced filtering and pagination.

Designed with a clean separation of concerns utilizing the **Repository Pattern** and a **Service Layer**, keeping the codebase highly maintainable, testable, and database-agnostic.

### 🔗 Live Demo

| | Link |
|---|---|
| 🌐 **Frontend** | [linkedin-insights-eosin.vercel.app](https://linkedin-insights-eosin.vercel.app) |
| ⚡ **Backend API** | [linkedin-insights-acmu.onrender.com](https://linkedin-insights-acmu.onrender.com) |
| 📖 **Swagger Docs** | [linkedin-insights-acmu.onrender.com/docs](https://linkedin-insights-acmu.onrender.com/docs) |
| 🗄️ **Database** | Aiven Cloud MySQL 8.0 |

> ⚠️ **Note**: The backend is deployed on **Render's free tier**. After periods of inactivity, the server spins down and the first request may take **up to 50 seconds** to cold-start. Subsequent requests are fast.

---

### Screenshots

![Posts](docs/screenshots/Posts.png)

![Top Posts](docs/screenshots/top-posts.png)

![Comments](docs/screenshots/comments.png)

![Employees](docs/screenshots/Employees.png)

![Search History](docs/screenshots/history.png)

---

## Key Features

- **Decoupled Configuration**: Decoupled environment variables using Pydantic Settings.
- **Repository + Service Architecture**: 
  - **Routers**: Handle HTTP requests, routing, caching, and serialization.
  - **Services**: Coordinate scraping, cache checks, and database updates.
  - **Repositories**: Encapsulate queries and SQL execution.
- **Cascading Scraper Design**: Uses the `linkedin-api` package (Voyager API wrapper) as the primary scraping layer. If credentials aren't configured or a rate limit occurs, it falls back to public HTML scraping, pre-defined seed company data, and finally structured placeholder generation.
- **Relational Integrity**: Tracks `pages`, `posts`, `comments`, and `employees` with full foreign keys and cascade delete logic.
- **Advanced Filtering & Pagination**: Support for pagination (`page` & `size` query params) combined with filters like follower ranges, industry matching, employee job title searching, and post sorting.
- **HTTP-Agnostic Exception Handling**: Domain exceptions are mapped to HTTP status codes globally at the FastAPI router level.
- **Comprehensive Testing Suite**: Automatic tests running on an in-memory SQLite database setup.

---

## Directory Structure

```
linkedin-insights/
├── app/
│   ├── models/          # SQLAlchemy Database Models
│   ├── schemas/         # Pydantic Request/Response Models
│   ├── repositories/    # Database queries and operations (CRUD)
│   ├── services/        # Business logic & Scraper cascade
│   ├── routers/         # API Endpoint routes
│   ├── utils/           # Shared exceptions & helpers
│   ├── config.py        # Environment configuration loader
│   ├── database.py      # SQLAlchemy connection & DB dependency
│   └── main.py          # FastAPI app initialization
├── docs/                # API guidelines and guides
├── tests/               # pytest suite
├── requirements.txt     # Dependencies
└── .env                 # Environment variables
```

---

## Tech Stack

- **FastAPI** — Asynchronous REST APIs with OpenAPI swagger generation.
- **SQLAlchemy 2.0** — Type-safe modern ORM mapping.
- **PyMySQL** — Python MySQL client.
- **Pydantic v2** — Data parsing and verification.
- **BeautifulSoup4** — Public HTML scraping.
- **Pytest** — Automated testing.


---

## Docker Setup

The backend is fully containerized using **Docker** and **Docker Compose**.

### Running with Docker Compose (Recommended)
This spins up both the FastAPI app and a local MySQL 8.0 database:
```bash
docker-compose up --build
```
- The `db` service starts a MySQL container with a health check.
- The `web` service waits for MySQL to be healthy before starting (`depends_on: condition: service_healthy`).
- Access the API at `http://localhost:8000`.

### Running with Docker Only (BYO Database)
If you have an external MySQL instance (e.g., Aiven, RDS):
```bash
docker build -t linkedin-insights .
docker run -p 8000:8000 \
  -e DATABASE_URL="mysql+pymysql://user:pass@host:port/dbname" \
  -e APP_ENV=production \
  linkedin-insights
```

### Dockerfile Highlights
- **Base Image**: `python:3.11-slim` — minimal footprint.
- **Build Dependencies**: Installs `build-essential` for compiling native extensions, then cleans up apt cache.
- **Production Server**: Runs `uvicorn` directly (no Gunicorn wrapper needed for single-instance Render deployment).

---

## Deployment Challenges & Fixes

Deploying to a cloud stack (Render + Aiven + Vercel) introduced real-world issues that don't surface in local development:

### 1. MySQL SSL Authentication (`ssl-mode` parameter)
Aiven provides a `DATABASE_URL` with `?ssl-mode=REQUIRED` appended. PyMySQL does **not** support `ssl-mode` as a URL query parameter — it causes a `TypeError` at connection time. The fix was to strip the query parameter from the URL and inject SSL configuration programmatically via SQLAlchemy's `connect_args` in `database.py`.

### 2. Missing `cryptography` Package
Aiven MySQL uses `caching_sha2_password` authentication. PyMySQL requires the `cryptography` package to handle this auth method, but it's not installed by default. Locally this didn't surface because local MySQL uses `mysql_native_password`. Added `cryptography` to `requirements.txt`.

### 3. CORS for Cross-Origin Frontend
The frontend (Vercel, `*.vercel.app`) and backend (Render, `*.onrender.com`) are on different origins. Without proper CORS middleware configuration, browsers block the API responses. Configured FastAPI's `CORSMiddleware` to allow the Vercel origin.

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.11+
- Running MySQL instance (local or cloud-hosted).

### 2. Installation
Clone this repository and open the directory:
```bash
git clone <https://github.com/Adityas3111N/Linkedin_Insights.git>
cd Linkedin-insights
```

Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Copy the sample environment file to `.env` and fill in your database/LinkedIn configurations:
```bash
cp .env.example .env
```
Or create a `.env` file in the root directory:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/linkedin_insights
APP_ENV=development
APP_DEBUG=True
API_V1_STR=/api/v1
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=
```

*Note: Create the database `linkedin_insights` inside your MySQL server before running the app. Tables are created automatically on startup.*

### 4. Running the Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Access the API: `http://127.0.0.1:8000`
- Access Swagger Docs: `http://127.0.0.1:8000/docs`

---

## Running the Tests

The test suite runs on an isolated, in-memory **SQLite database**. You do **NOT** need MySQL configured to execute tests:

```bash
pytest -v
```

---

## API Documentation Summary

### System Health
- `GET /health` — Verifies database connection responsiveness and server status.

### Company Pages
- `GET /api/v1/pages` — Paginated list of pages. Supports filters:
  - `name`: partial case-insensitive match (e.g. `?name=deep`).
  - `industry`: exact match (e.g. `?industry=Software`).
  - `min_followers` / `max_followers` (e.g. `?min_followers=20000`).
- `GET /api/v1/pages/{page_id}` — Get single page details. **Scrapes in real-time from LinkedIn if missing from the local database**.
- `POST /api/v1/pages/{page_id}/scrape` — Forces a real-time scraping refresh, updating existing database entries.

### Sub-Collections (Paginated)
- `GET /api/v1/pages/{page_id}/posts` — Retrieve recent posts cached for a page. Supports `sort=latest` or `sort=top` (by likes).
- `GET /api/v1/pages/{page_id}/employees` — Retrieve employees working at the company. Supports filtering by job `title` (e.g., `?title=Engineer`).
- `GET /api/v1/pages/{page_id}/posts/{post_id}/comments` — Retrieve comments for a specific post.

---

## Design Journey: Handling the LinkedIn Auth Wall

Initially, I tried scraping public LinkedIn pages directly using `httpx` and `BeautifulSoup4`. However, LinkedIn aggressively redirects unauthenticated traffic to an auth wall after a few requests, rendering raw HTML scraping useless in production.

I evaluated three options to handle this:
1. **Headless Browsers (Playwright/Selenium)**: Slow, heavy, and overkill for a simple microservice.
2. **Paid API Proxies**: Reliable, but introduces external costs and API key management.
3. **Lightweight Authenticated Wrapper + Cascade Fallback**: What I implemented.

I chose the cascade approach. If LinkedIn credentials are in `.env`, it queries LinkedIn's internal Voyager API wrapper for real-time posts, comments, and employees. If credentials are missing, it falls back to a public HTML parse attempt, followed by pre-defined seed data, and finally structured placeholder generation. This ensures the app is highly resilient and always displays structured data to the user without crashing.

---

## Architecture & Performance Decisions

1. **Layered Decoupling**
   - Database transactions are separated from business logic. If we migrate from MySQL to PostgreSQL or SQLite, only the Repository layer changes. The Service layer, routers, and application logic remain completely untouched.

2. **In-Memory & DB Caching**
   - Scraping is I/O heavy. We use local database storage combined with a short-lived (5-minute TTL) in-memory cache at the router layer to keep response times sub-millisecond for popular requests and protect against redundant network calls.

3. **Connection Management**
   - FastAPI's dependency injection (`Depends(get_db)`) manages database sessions as a generator (`yield`). This guarantees that SQLAlchemy sessions are cleanly closed (`db.close()`) after a request finishes, preventing connection leaks.


