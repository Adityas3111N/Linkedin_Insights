import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.page import PageResponse, PageDetailResponse, PageListFilters
from app.schemas.post import PostResponse
from app.schemas.employee import EmployeeResponse
from app.schemas.comment import CommentResponse
from app.services.page_service import PageService

router = APIRouter(prefix="/pages", tags=["LinkedIn Pages"])
page_service = PageService()

# Simple cache for page details: {page_id: (expiry, PageDetailResponse)}
_details_cache = {}
CACHE_TTL = 300


@router.get("", response_model=PaginatedResponse[PageResponse])
def get_pages(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    industry: Optional[str] = Query(None),
    min_followers: Optional[int] = Query(None, ge=0),
    max_followers: Optional[int] = Query(None, ge=0),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    filters = PageListFilters(
        industry=industry,
        min_followers=min_followers,
        max_followers=max_followers,
        name=name
    )
    skip = (page - 1) * size
    total, items = page_service.list_pages(db, skip=skip, limit=size, filters=filters)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=items
    )


@router.get("/{page_id}", response_model=PageDetailResponse)
def get_page_details(
    page_id: str = Path(...),
    db: Session = Depends(get_db)
):
    now = time.time()
    if page_id in _details_cache:
        expiry, cached_val = _details_cache[page_id]
        if now < expiry:
            return cached_val

    page = page_service.get_page_details(db, page_id)
    
    data = PageDetailResponse(
        id=page.id,
        page_id=page.page_id,
        name=page.name,
        url=page.url,
        linkedin_id=page.linkedin_id,
        profile_pic_url=page.profile_pic_url,
        description=page.description,
        website=page.website,
        industry=page.industry,
        follower_count=page.follower_count,
        head_count=page.head_count,
        specialities=page.specialities,
        founded=page.founded,
        created_at=page.created_at,
        updated_at=page.updated_at,
        recent_posts=page.posts[:10] if page.posts else [],
        recent_employees=page.employees[:10] if page.employees else []
    )

    _details_cache[page_id] = (now + CACHE_TTL, data)
    return data


@router.post("/{page_id}/scrape", response_model=PageDetailResponse, status_code=status.HTTP_201_CREATED)
def force_refresh_page(
    page_id: str = Path(...),
    db: Session = Depends(get_db)
):
    page = page_service.force_refresh_page(db, page_id)
    data = PageDetailResponse(
        id=page.id,
        page_id=page.page_id,
        name=page.name,
        url=page.url,
        linkedin_id=page.linkedin_id,
        profile_pic_url=page.profile_pic_url,
        description=page.description,
        website=page.website,
        industry=page.industry,
        follower_count=page.follower_count,
        head_count=page.head_count,
        specialities=page.specialities,
        founded=page.founded,
        created_at=page.created_at,
        updated_at=page.updated_at,
        recent_posts=page.posts[:10] if page.posts else [],
        recent_employees=page.employees[:10] if page.employees else []
    )
    _details_cache[page_id] = (time.time() + CACHE_TTL, data)
    return data


@router.get("/{page_id}/posts", response_model=PaginatedResponse[PostResponse])
def get_page_posts(
    page_id: str = Path(...),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=25),
    sort: str = Query("latest"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    total, items = page_service.get_page_posts(db, page_id, skip=skip, limit=size, sort=sort)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=items
    )


@router.get("/{page_id}/employees", response_model=PaginatedResponse[EmployeeResponse])
def get_page_employees(
    page_id: str = Path(...),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    title: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    total, items = page_service.get_page_employees(db, page_id, skip=skip, limit=size, title=title)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=items
    )


@router.get("/{page_id}/posts/{post_id}/comments", response_model=PaginatedResponse[CommentResponse])
def get_post_comments(
    page_id: str = Path(...),
    post_id: int = Path(...),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    total, items = page_service.get_post_comments(db, page_id, post_id, skip=skip, limit=size)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=items
    )
