from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.post import PostResponse
from app.schemas.employee import EmployeeResponse


class PageBase(BaseModel):
    page_id: str
    name: str
    url: Optional[str] = None
    linkedin_id: Optional[str] = None
    profile_pic_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    follower_count: int = 0
    head_count: int = 0
    specialities: Optional[List[str]] = None
    founded: Optional[str] = None


class PageCreate(PageBase):
    pass


class PageResponse(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PageDetailResponse(PageResponse):
    recent_posts: List[PostResponse] = []
    recent_employees: List[EmployeeResponse] = []


class PageListFilters(BaseModel):
    industry: Optional[str] = None
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    name: Optional[str] = None
