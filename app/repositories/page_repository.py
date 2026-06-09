from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.page import Page
from app.schemas.page import PageListFilters


class PageRepository:
    def find_by_id(self, db: Session, id: int) -> Optional[Page]:
        return db.get(Page, id)

    def find_by_page_id(self, db: Session, page_id: str) -> Optional[Page]:
        stmt = select(Page).where(Page.page_id == page_id)
        return db.execute(stmt).scalar_one_or_none()

    def find_all(
        self, db: Session, skip: int, limit: int, filters: PageListFilters
    ) -> Tuple[int, List[Page]]:
        query = select(Page)

        if filters.industry:
            query = query.where(Page.industry == filters.industry)
        if filters.min_followers is not None:
            query = query.where(Page.follower_count >= filters.min_followers)
        if filters.max_followers is not None:
            query = query.where(Page.follower_count <= filters.max_followers)
        if filters.name:
            query = query.where(Page.name.ilike(f"%{filters.name}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar_one()

        query = query.offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return total, list(items)

    def create(self, db: Session, data: dict) -> Page:
        page = Page(**data)
        db.add(page)
        db.commit()
        db.refresh(page)
        return page

    def update(self, db: Session, page: Page, data: dict) -> Page:
        for field, value in data.items():
            setattr(page, field, value)
        db.commit()
        db.refresh(page)
        return page

    def delete(self, db: Session, page: Page) -> None:
        db.delete(page)
        db.commit()
