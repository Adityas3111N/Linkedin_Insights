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


@router.get("", response_model=PaginatedResponse[PageResponse])
def get_pages(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    min_followers: Optional[int] = Query(None, ge=0, description="Minimum follower count"),
    max_followers: Optional[int] = Query(None, ge=0, description="Maximum follower count"),
    name: Optional[str] = Query(None, description="Partial name search (case-insensitive)"),
    db: Session = Depends(get_db)
):
    """Retrieve a paginated and filtered list of stored LinkedIn pages."""
    # Pack parameters into validation filter schema
    filters = PageListFilters(
        industry=industry,
        min_followers=min_followers,
        max_followers=max_followers,
        name=name
    )
    
    # Calculate SQL OFFSET limit
    skip = (page - 1) * size
    
    total, results = page_service.list_pages(db, skip=skip, limit=size, filters=filters)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=results
    )


import time

# Simple in-memory cache for page details: {page_id: (expiry_timestamp, PageDetailResponse)}
_details_cache = {}
CACHE_TTL = 300 # 5 minutes


@router.get("/{page_id}", response_model=PageDetailResponse)
def get_page_details(
    page_id: str = Path(..., description="The LinkedIn URL slug / Page ID (e.g. 'deepsolv')"),
    db: Session = Depends(get_db)
):
    """Fetch details of a single page. Scrapes LinkedIn in real-time if not cached in database."""
    now = time.time()
    if page_id in _details_cache:
        expiry, cached_val = _details_cache[page_id]
        if now < expiry:
            return cached_val

    page = page_service.get_page_details(db, page_id)
    
    # Structure the detail response dynamically by loading relationships
    # We take top 10 recent posts and top 10 employees for page details view
    response_data = PageDetailResponse(
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

    # Cache the structured response
    _details_cache[page_id] = (now + CACHE_TTL, response_data)
    return response_data


@router.post("/{page_id}/scrape", response_model=PageDetailResponse, status_code=status.HTTP_201_CREATED)
def force_refresh_page(
    page_id: str = Path(..., description="The LinkedIn URL slug to scrape"),
    db: Session = Depends(get_db)
):
    """Force an active real-time crawl of LinkedIn page details and overwrite existing entries."""
    page = page_service.force_refresh_page(db, page_id)
    response_data = PageDetailResponse(
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
    # Update cache
    _details_cache[page_id] = (time.time() + CACHE_TTL, response_data)
    return response_data



@router.get("/{page_id}/posts", response_model=PaginatedResponse[PostResponse])
def get_page_posts(
    page_id: str = Path(..., description="The LinkedIn URL slug"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=25, description="Items per page"),
    sort: str = Query("latest", description="Sort order: 'latest' or 'top'"),
    db: Session = Depends(get_db)
):
    """Fetch paginated posts for a specific LinkedIn Page."""
    skip = (page - 1) * size
    total, results = page_service.get_page_posts(db, page_id, skip=skip, limit=size, sort=sort)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=results
    )


@router.get("/{page_id}/employees", response_model=PaginatedResponse[EmployeeResponse])
def get_page_employees(
    page_id: str = Path(..., description="The LinkedIn URL slug"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    title: Optional[str] = Query(None, description="Filter employees by job title"),
    db: Session = Depends(get_db)
):
    """Fetch paginated employees working at a specific LinkedIn Page."""
    skip = (page - 1) * size
    total, results = page_service.get_page_employees(db, page_id, skip=skip, limit=size, title=title)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=results
    )


@router.get("/{page_id}/posts/{post_id}/comments", response_model=PaginatedResponse[CommentResponse])
def get_post_comments(
    page_id: str = Path(..., description="The LinkedIn URL slug"),
    post_id: int = Path(..., description="The internal post database ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Fetch paginated comments for a specific post of a LinkedIn Page."""
    skip = (page - 1) * size
    total, results = page_service.get_post_comments(db, page_id, post_id, skip=skip, limit=size)
    total_pages = (total + size - 1) // size if total > 0 else 0

    return PaginatedResponse(
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        results=results
    )

