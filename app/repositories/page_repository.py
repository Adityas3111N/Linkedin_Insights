from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from app.models.page import Page
from app.schemas.page import PageListFilters


class PageRepository:
    """Encapsulates all database operations for the Page entity."""

    def find_by_id(self, db: Session, id: int) -> Optional[Page]:
        """Find a single page by its primary key."""
        return db.get(Page, id)

    def find_by_page_id(self, db: Session, page_id: str) -> Optional[Page]:
        """Find a single page by its unique slug ID (page_id)."""
        statement = select(Page).where(Page.page_id == page_id)
        return db.execute(statement).scalar_one_or_none()

    def find_all(
        self, db: Session, skip: int, limit: int, filters: PageListFilters
    ) -> Tuple[int, List[Page]]:
        """Fetch a paginated list of Page records matching optional query filters.

        Args:
            db: Active database session.
            skip: Offset/number of records to skip.
            limit: Limit/maximum records to fetch.
            filters: Filter options (name, industry, min_followers, max_followers).

        Returns:
            A tuple of (total_matching_count, list_of_matching_pages).
        """
        query = select(Page)

        # Build dynamic queries depending on query filter arguments
        if filters.industry:
            query = query.where(Page.industry == filters.industry)
        
        if filters.min_followers is not None:
            query = query.where(Page.follower_count >= filters.min_followers)
            
        if filters.max_followers is not None:
            query = query.where(Page.follower_count <= filters.max_followers)
            
        if filters.name:
            # Case-insensitive partial matches search
            query = query.where(Page.name.ilike(f"%{filters.name}%"))

        # 1. Get the total count of matches BEFORE offset/limit slicing
        count_query = select(func.count()).select_from(query.subquery())
        total_count = db.execute(count_query).scalar_one()

        # 2. Slice result page
        query = query.offset(skip).limit(limit)
        results = db.execute(query).scalars().all()

        return total_count, list(results)

    def create(self, db: Session, page_data: dict) -> Page:
        """Insert a new Page record into the database."""
        page = Page(**page_data)
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    def update(self, db: Session, page: Page, update_data: dict) -> Page:
        """Update fields of an existing Page instance."""
        for field, value in update_data.items():
            setattr(page, field, value)
        db.commit()
        db.refresh(page)
        return page

    def delete(self, db: Session, page: Page) -> None:
        """Remove a Page record.

        Cascade options handle related posts, comments, and employees at the database level.
        """
        db.delete(page)
        db.commit()
