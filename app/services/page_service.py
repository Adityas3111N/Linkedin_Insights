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
from app.utils.exceptions import PageNotFoundException, PostNotFoundException

logger = logging.getLogger(__name__)


class PageService:
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
        page = self.page_repo.find_by_page_id(db, page_id)
        if page:
            logger.info(f"DB cache hit for page '{page_id}'")
            return page

        logger.info(f"DB cache miss, scraping '{page_id}'")
        return self.force_refresh_page(db, page_id)

    def force_refresh_page(self, db: Session, page_id: str) -> Page:
        scraped = self.scraper.scrape_all(page_id)
        if not scraped or not scraped.get("page"):
            raise PageNotFoundException(page_id)

        existing = self.page_repo.find_by_page_id(db, page_id)
        if existing:
            self.page_repo.delete(db, existing)
            db.flush()

        page_payload = {k: v for k, v in scraped["page"].items() if not k.startswith("_")}
        page = self.page_repo.create(db, page_payload)

        for post_item in scraped["posts"]:
            comments = post_item.pop("comments", [])
            post_item["page_id"] = page.id
            post = self.post_repo.create(db, post_item)
            
            if comments:
                for comment in comments:
                    comment["post_id"] = post.id
                self.comment_repo.bulk_create(db, comments)

        employees = scraped["employees"]
        if employees:
            for emp in employees:
                emp["page_id"] = page.id
            self.employee_repo.bulk_create(db, employees)

        return page

    def list_pages(
        self, db: Session, skip: int, limit: int, filters: PageListFilters
    ) -> Tuple[int, List[Page]]:
        return self.page_repo.find_all(db, skip, limit, filters)

    def get_page_posts(self, db: Session, page_id: str, skip: int, limit: int, sort: str = "latest") -> Tuple[int, List[Post]]:
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
        return self.post_repo.find_all_by_page_id(db, page.id, skip, limit, sort=sort)

    def get_page_employees(self, db: Session, page_id: str, skip: int, limit: int, title: str = None) -> Tuple[int, List[Employee]]:
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
        return self.employee_repo.find_all_by_page_id(db, page.id, skip, limit, title=title)

    def get_post_comments(self, db: Session, page_id: str, post_id: int, skip: int, limit: int) -> Tuple[int, list]:
        page = self.page_repo.find_by_page_id(db, page_id)
        if not page:
            raise PageNotFoundException(page_id)
        
        post = self.post_repo.find_by_id(db, post_id)
        if not post or post.page_id != page.id:
            raise PostNotFoundException(post_id)
            
        return self.comment_repo.find_all_by_post_id(db, post.id, skip, limit)
