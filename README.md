# LinkedIn Insights Microservice

A production-grade backend microservice built with **FastAPI**, **SQLAlchemy 2.0**, and **MySQL**. It crawls LinkedIn company pages in real-time, caches data into a structured relational database, and exposes clean RESTful APIs with advanced filtering and pagination.

Designed with a strict separation of concerns utilizing the **Repository Pattern** and a **Service Layer**, keeping the codebase highly maintainable, testable, and database-agnostic.

---

## Key Features

- **Twelve-Factor App Configuration**: Environment-specific configurations are completely decoupled from application logic.
- **Repository + Service Architecture**: 
  - **Routers**: HTTP concerns only.
  - **Services**: Orchestrates database transactions and scrapes.
  - **Repositories**: Encapsulates DB-specific queries.
- **Real-Time Scraping & Deterministic Mock Fallback**: Uses `httpx` and `BeautifulSoup4` to parse public LinkedIn data. If rate-limited or blocked, it gracefully triggers a mock fallback dataset, ensuring demos and tests run successfully.
- **Relational Integrity**: Complete schema layout tracking `pages`, `posts`, `comments`, and `employees` with foreign key database-level cascade controls.
- **Advanced API Filtering & Pagination**: Paginated listing endpoints with query parameters for followers ranges, exact industry matches, and case-insensitive partial name searches.
- **HTTP-Agnostic Error Handling**: The business logic raises domain exceptions that are dynamically mapped to HTTP status codes at the router layer using FastAPI global handlers.
- **Comprehensive Testing Suite**: 7 unit/integration tests running on an in-memory SQLite database setup.

---

## Folder Structure

```
linkedin-insights/
├── app/
│   ├── models/          # SQLAlchemy Database ORM Models
│   ├── schemas/         # Pydantic v2 Request/Response Schemas
│   ├── repositories/    # Encapsulated Database Queries (CRUD)
│   ├── services/        # Scraper & Business Logic orchestrators
│   ├── routers/         # FastAPI Endpoint Handlers
│   ├── utils/           # Shared helpers, custom exceptions
│   ├── config.py        # Centralized settings loader
│   ├── database.py      # SQLAlchemy connection & DB dependencies
│   └── main.py          # FastAPI app initialization & exception handlers
├── docs/                # Architectural, DB, & API specifications
├── tests/               # pytest suite (isolated memory DBs)
├── requirements.txt     # Locked dependencies
└── .env                 # Environment variables template
```

---

## Tech Stack & Dependencies

- **FastAPI** (`0.115.0`) — Asynchronous REST APIs, validation, and interactive OpenAPI documentation.
- **SQLAlchemy** (`2.0.35`) — Modern Python SQL toolkit with type-safe mapped columns.
- **PyMySQL** (`1.1.1`) — Native Python MySQL connector.
- **Cryptography** (`48.0.0`) — Required for MySQL 8 authentication encryption protocol.
- **Pydantic** (`2.9.2`) — Core data parsing and verification.
- **BeautifulSoup4** (`4.12.3`) — Scraping parser.
- **Pytest** (`8.3.3`) — Automated test suites.

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.11 or higher installed on your machine.
- A running MySQL instance (local or hosted on a cloud provider like Aiven, Railway, Render, etc.).

### 2. Installation
Clone this repository and open the directory:
```bash
git clone <your-repository-url>
cd Linkedin-insights
```

Create and activate a Python virtual environment:
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env` variables template and modify configurations:
Create a `.env` file in the root directory:
```env
# Local MySQL setup:
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/linkedin_insights

# Cloud DB setup (e.g., Aiven MySQL or Railway):
# DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<database>

APP_ENV=development
APP_DEBUG=True
API_V1_STR=/api/v1
```

*Note: You must manually create the database named `linkedin_insights` inside your MySQL server before running the app. Tables are created automatically on startup.*

### 4. Running the Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Access the API at: `http://127.0.0.1:8000`
- Access the interactive documentation (Swagger UI) at: `http://127.0.0.1:8000/docs`

---

## Running the Tests

The test suite runs on an isolated, in-memory **SQLite database**. You do **NOT** need MySQL running or configured to execute tests:

```bash
# Run all tests with verbose output
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
  - `min_followers` / `max_followers` (e.g. `?min_followers=20000&max_followers=50000`).
- `GET /api/v1/pages/{page_id}` — Get single page details. **Scrapes in real-time from LinkedIn if missing from the cache DB**.
- `POST /api/v1/pages/{page_id}/scrape` — Forces a real-time scraping refresh, updating existing rows.

### Nested Sub-Collections (Paginated)
- `GET /api/v1/pages/{page_id}/posts` — Retrieve recent posts cached for a page.
- `GET /api/v1/pages/{page_id}/employees` — Retrieve list of scraped employees working at the company.

---

## Key Interview Talking Points (How to Ace the Interview)

1. **"Why the Repository Pattern?"**
   - *"I decoupled SQL transactions from business logic. If we transition from MySQL to PostgreSQL or MongoDB in the future, we only swap or rewrite the Repository layer. The Service layer, routers, and application logic remain completely untouched."*

2. **"How do you handle LinkedIn blocking scrapers?"**
   - *"LinkedIn blocks anonymous scrapers aggressively. I engineered the `ScraperService` to first attempt a live HTML scrape using customized user-agents. If blocked or rate-limited, it falls back on a deterministic, structured simulation dataset. This ensures that the frontend/APIs remain operational and demo-able under any network condition."*

3. **"How do you prevent connection leaks?"**
   - *"I use FastAPI's dependency injection (`Depends(get_db)`) to inject SQLAlchemy sessions. It's written as a Python generator (`yield`), which guarantees that SQLAlchemy sessions are cleanly closed (`db.close()`) after a request finishes, even if the API route raises an unhandled exception."*

4. **"How are database schemas structured for performance?"**
   - *"We use auto-incrementing integers as Primary Keys for faster indexed joins, while storing the URL slug `page_id` as a unique index key for rapid lookup. We also added indices to filterable fields (`follower_count`, `industry`, `name`) to prevent full table scans when queries grow."*
