# Database Design

## Overview
MySQL 8.x database named `linkedin_insights`. Four tables with foreign key relationships.

## Entity Relationship

```
pages (1) ──────< posts (many)
                      │
                      └────< comments (many)

pages (1) ──────< employees (many)
```

- One page has many posts
- One post has many comments
- One page has many employees
- Deleting a page cascades to all related posts, comments, and employees

## Tables

### `pages`
Stores LinkedIn company page information.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INT | PK, AUTO_INCREMENT | Internal ID, never exposed in API |
| page_id | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | URL slug (e.g., "deepsolv") |
| name | VARCHAR(500) | NOT NULL | Company display name |
| url | VARCHAR(1000) | | Full LinkedIn URL |
| linkedin_id | VARCHAR(100) | | Platform-specific numeric ID |
| profile_pic_url | TEXT | | URL to profile picture |
| description | TEXT | | Company "About" section |
| website | VARCHAR(500) | | Company website URL |
| industry | VARCHAR(255) | INDEX | Industry category |
| follower_count | INT | INDEX, DEFAULT 0 | Total followers |
| head_count | INT | DEFAULT 0 | Number of employees |
| specialities | JSON | | JSON array of strings |
| founded | VARCHAR(50) | | Year founded |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When we first scraped this page |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | Last time data was refreshed |

### `posts`
Stores LinkedIn posts made by a company page.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INT | PK, AUTO_INCREMENT | |
| page_id | INT | FK → pages.id, ON DELETE CASCADE | Which page made this post |
| content | TEXT | | Post text content |
| post_url | VARCHAR(1000) | | Direct link to the post |
| likes_count | INT | DEFAULT 0 | |
| comments_count | INT | DEFAULT 0 | |
| shares_count | INT | DEFAULT 0 | |
| media_url | VARCHAR(1000) | | Attached image/video URL |
| media_type | VARCHAR(50) | | "image", "video", "article", or "none" |
| posted_at | DATETIME | | When the post was published on LinkedIn |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When we scraped this post |

### `comments`
Stores comments on LinkedIn posts.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INT | PK, AUTO_INCREMENT | |
| post_id | INT | FK → posts.id, ON DELETE CASCADE | Which post this comment belongs to |
| author_name | VARCHAR(255) | | Commenter's display name |
| author_profile_url | VARCHAR(1000) | | Link to commenter's profile |
| text | TEXT | | Comment content |
| commented_at | DATETIME | | When the comment was posted |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When we scraped this comment |

### `employees`
Stores people who work at the company.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INT | PK, AUTO_INCREMENT | |
| page_id | INT | FK → pages.id, ON DELETE CASCADE | Which company they work at |
| name | VARCHAR(255) | NOT NULL | Employee's display name |
| title | VARCHAR(500) | | Job title |
| profile_url | VARCHAR(1000) | | Link to their LinkedIn profile |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | When we scraped this employee |

## Indexes

| Table | Column(s) | Why |
|-------|-----------|-----|
| pages | page_id | Unique lookups by slug — every API call uses this |
| pages | follower_count | Range filtering: "find pages with 20k-40k followers" |
| pages | industry | Equality filtering: "find all Technology pages" |
| pages | name | LIKE searches: "find pages matching 'deep'" |
| posts | page_id | JOINs: "get all posts for this page" |
| comments | post_id | JOINs: "get all comments for this post" |
| employees | page_id | JOINs: "get all employees for this page" |

## Design Decisions

**Why integer PK + string unique key?**
Integer primary keys are faster for JOINs and indexing (4 bytes vs variable-length string). The `page_id` string is the human-readable identifier used in API URLs.

**Why JSON for specialities?**
It's a simple list of strings like `["AI", "Machine Learning", "Data Science"]`. Creating a separate `specialities` table with a junction table adds two tables and a JOIN for minimal benefit. MySQL's JSON type handles this cleanly.

**Why CASCADE deletes?**
When you remove a company page from the system, its posts, comments, and employees should go too. Orphaned rows with broken foreign keys cause data integrity issues.

**Why separate created_at and posted_at on posts?**
`posted_at` = when the post was published on LinkedIn (their timestamp).
`created_at` = when our scraper found and saved it (our timestamp).
These are different events and both are useful for debugging.
