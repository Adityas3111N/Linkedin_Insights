from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from app.schemas.post import PostResponse
from app.schemas.employee import EmployeeResponse


class PageBase(BaseModel):
    page_id: str = Field(..., description="Unique URL slug representing the page ID (e.g., 'deepsolv')")
    name: str = Field(..., description="Display name of the company page")
    url: Optional[str] = Field(None, description="Full LinkedIn URL of the page")
    linkedin_id: Optional[str] = Field(None, description="LinkedIn platform-specific numerical ID")
    profile_pic_url: Optional[str] = Field(None, description="URL of the profile image")
    description: Optional[str] = Field(None, description="Full description of the company")
    website: Optional[str] = Field(None, description="Official website URL")
    industry: Optional[str] = Field(None, description="Industry category")
    follower_count: int = Field(0, description="Total number of followers")
    head_count: int = Field(0, description="Self-reported employee headcount range/exact value")
    specialities: Optional[List[str]] = Field(None, description="List of company specialities")
    founded: Optional[str] = Field(None, description="Year or description of when it was founded")


class PageCreate(PageBase):
    pass


class PageResponse(PageBase):
    id: int = Field(..., description="Internal database primary key")
    created_at: datetime = Field(..., description="Datetime when we first crawled this page")
    updated_at: datetime = Field(..., description="Datetime when this page record was last refreshed")

    model_config = ConfigDict(from_attributes=True)


class PageDetailResponse(PageResponse):
    """Detailed response carrying sub-entities such as recent posts and employees."""
    
    recent_posts: List[PostResponse] = Field(default=[], description="List of recent posts cached for this page")
    recent_employees: List[EmployeeResponse] = Field(default=[], description="List of employees working at the company")


class PageListFilters(BaseModel):
    """Schema to parse and validate optional query parameters for page filtering."""
    
    industry: Optional[str] = Field(None, description="Filter by exact industry match")
    min_followers: Optional[int] = Field(None, description="Filter by minimum follower count")
    max_followers: Optional[int] = Field(None, description="Filter by maximum follower count")
    name: Optional[str] = Field(None, description="Case-insensitive partial match search on page name")
