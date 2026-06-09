import logging
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.page import Page
from app.models.post import Post
from app.models.employee import Employee
from app.repositories.page_repository import PageRepository
from app.repositories.post_repository import PostRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.scraper_service import ScraperService
from app.schemas.page import PageListFilters
from app.utils.exceptions import PageNotFoundException

logger = logging.getLogger(__name__)


class PageService:
    """Orchestrates database repositories and scraping interactions."""

    def __init__(self):
        self.page_repo = PageRepository()
        self.post_repo = PostRepository()
        self.comment_repo = CommentRepository()
        self.employee_repo = EmployeeRepository()
        from app.config import settings
        self.scraper = ScraperService(
            linkedin_email=settings.LINKEDIN_EMAIL,
            linkedin_password=settings.LINKEDIN_PASSWORD
        )

    def get_page_details(self, db: Session, page_id: str) -> Page:
        """Fetch page details by ID. Scrapes LinkedIn if not found in database."""
        page = self.page_repo.find_by_page_id(db, page_id)
        
        if page:
            logger.info(f"Cache hit: Found Page record for '{page_id}' in the database.")
            return page

        # Cache miss -> trigger scraping process
        logger.info(f"Cache miss: Scraping LinkedIn page '{page_id}' in real-time.")
        return self.force_refresh_page(db, page_id)

    def force_refresh_page(self, db: Session, page_id: str) -> Page:
        """Forces scraping of page data and updates/overwrites existing database rows."""
        # 1. Scrape all entities (Page, posts, comments, employees)
        scraped_data = self.scraper.scrape_all(page_id)
        
        if not scraped_data or not scraped_data.get("page"):
            raise PageNotFoundException(page_id)

        # 2. Check if page already exists to do update vs create
        existing_page = self.page_repo.find_by_page_id(db, page_id)
        
        if existing_page:
            # Delete old relationships to prevent duplicates
            self.page_repo.delete(db, existing_page)
            db.flush()

        # 3. Save new parent Page record (strip internal scraper metadata)
        page_payload = {
            key: value
            for key, value in scraped_data["page"].items()
            if not key.startswith("_")
        }
        page = self.page_repo.create(db, page_payload)

        # 4. Save related posts and their comments
        for post_item in scraped_data["posts"]:
            comments_to_save = post_item.pop("comments", [])
            post_item["page_id"] = page.id
            
            # Save single post
            post = self.post_repo.create(db, post_item)
            
            # Save corresponding comments
            if comments_to_save:
                for comment in comments_to_save:
                    comment["post_id"] = post.id
                self.comment_repo.bulk_create(db, comments_to_save)

        # 5. Save related employees
        employees_to_save = scraped_data["employees"]
        if employees_to_save:
            for emp in employees_to_save:
                emp["page_id"] = page.id
            self.employee_repo.bulk_create(db, employees_to_save)

        return page

    def list_pages(
        self, db: Session, skip: int, limit: int, filters: PageListFilters
    ) -> Tuple[int, List[Page]]:
        """Retrieve a paginated and filtered list of company pages."""
        return self.page_repo.find_all(db, skip, limit, filters)

    def get_page_posts(self, db: Session, page_id: str, skip: int, limit: int, sort: str = "latest") -> Tuple[int, List[Post]]:
        """Get paginated posts for a specific page slug."""
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
        
        return self.post_repo.find_all_by_page_id(db, page.id, skip, limit, sort=sort)

    def get_page_employees(self, db: Session, page_id: str, skip: int, limit: int, title: str = None) -> Tuple[int, List[Employee]]:
        """Get paginated employees for a specific page slug."""
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
            
        return self.employee_repo.find_all_by_page_id(db, page.id, skip, limit, title=title)

    def get_post_comments(self, db: Session, page_id: str, post_id: int, skip: int, limit: int) -> Tuple[int, list]:
        """Get paginated comments for a specific post within a page."""
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
        
        # Verify the post exists and belongs to this page
        post = self.post_repo.find_by_id(db, post_id)
        if not post or post.page_id != page.id:
            from app.utils.exceptions import PostNotFoundException
            raise PostNotFoundException(post_id)
            
        return self.comment_repo.find_all_by_post_id(db, post.id, skip, limit)

