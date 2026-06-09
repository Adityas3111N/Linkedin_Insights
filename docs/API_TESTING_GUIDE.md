# LinkedIn Insights — API Coverage & Testing Guide

This guide maps each requirement of the SDE Assignment to the corresponding API endpoint, explains how it is verified in the Frontend UI, and lists the steps to test every single one.

---

## 📋 API Requirement Mapping

| Assignment Requirement | Backend API Endpoint | Frontend UI Coverage |
| :--- | :--- | :--- |
| **Get Page Details (Cached/Realtime)** | `GET /api/v1/pages/{page_id}` | Main Search Bar (renders profile banner, stats, description) |
| **Force Scrape Page** | `POST /api/v1/pages/{page_id}/scrape` | Used to trigger a fresh crawl and bypass/overwrite cache |
| **Filter Stored Pages (Followers, Name, Industry)** | `GET /api/v1/pages` | Stored Pages Table (automatically populates at bottom of screen) |
| **List Page Posts (Paginated)** | `GET /api/v1/pages/{page_id}/posts` | Recent Posts section (with custom paginated scrolling controls) |
| **List Post Comments (Paginated)** | `GET /api/v1/pages/{page_id}/posts/{post_id}/comments` | Comments popup modal (loads dynamically when clicking a post) |
| **List Employees (Paginated)** | `GET /api/v1/pages/{page_id}/employees` | People section (with custom paginated grid controls) |
| **System Health & DB Check** | `GET /health` | Validates API server is active and DB connection is live |

---

## 🧪 How to Test on Frontend

Here is how you can use the Frontend UI to trigger and verify every endpoint:

### 1. Test Realtime Scrape / Fetch Details (`GET /api/v1/pages/{page_id}`)
* **How to trigger**: Type a page slug like `google`, `microsoft`, or `deepsolv` into the search input and click **Search**.
* **What it tests**: If the page is not in the database, the backend scrapes LinkedIn (using Layer 1 linkedin-api if credentials are set, or HTML/Seed data fallback), saves it, and returns it. If it exists, it returns from cache instantly.
* **UI Verification**: Visualizes page banner, logo, industry, website link, and description.

### 2. Test Paginated Recent Posts (`GET /api/v1/pages/{page_id}/posts`)
* **How to trigger**: Search a page, then scroll down to **Recent Posts** and click **Previous / Next** pagination buttons.
* **What it tests**: Tests the database pagination of related posts (`posts?page=1&size=5`).

### 3. Test Paginated Post Comments (`GET /api/v1/pages/{page_id}/posts/{post_id}/comments`)
* **How to trigger**: On any post card, click the **💬 X Comments** button.
* **What it tests**: Triggers a popup modal that fetches comments belonging to that specific post dynamically from the database (`posts/{post_id}/comments?page=1&size=20`).

### 4. Test Paginated Employees (`GET /api/v1/pages/{page_id}/employees`)
* **How to trigger**: Scroll down to the **People** section and click the **Previous / Next** pagination buttons.
* **What it tests**: Tests the database pagination of employees (`employees?page=1&size=6`).

### 5. Test Listing Stored Pages with Filters (`GET /api/v1/pages`)
* **How to trigger**: Refresh the page or search a new company. The **Stored Pages** table at the bottom will automatically update with a list of all pages currently cached in the DB.
* **Click-to-Search**: Click any row in that table; the UI automatically copies the slug to the search bar and loads that page.

### 6. Test In-Memory Cache TTL (Bonus Requirement)
* **How to trigger**: Search for `deepsolv` twice in a row.
* **What it tests**: The first request queries the DB/scrapes. The second request returns instantly without any DB or network calls because the 5-minute cache TTL is active.

---

## 🛠️ Postman Collection
The collection is located at:
👉 [LinkedIn_Insights_Postman_Collection.json](file:///e:/Playground/Linkedin-insights/docs/LinkedIn_Insights_Postman_Collection.json)
You can directly import this file into Postman to test raw HTTP endpoints outside the browser!
