from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.comment import CommentResponse


class PostBase(BaseModel):
    content: Optional[str] = Field(None, description="The textual content of the post")
    post_url: Optional[str] = Field(None, description="URL of the specific post")
    likes_count: int = Field(0, description="Total reaction/like count")
    comments_count: int = Field(0, description="Total number of comments reported by LinkedIn")
    shares_count: int = Field(0, description="Total share count")
    media_url: Optional[str] = Field(None, description="Attached media item URL")
    media_type: Optional[str] = Field(None, description="Type of media, e.g., image, video, article, none")
    posted_at: Optional[datetime] = Field(None, description="When the post was published on LinkedIn")


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When this post was stored in our database")

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostResponse):
    comments: List[CommentResponse] = Field(default=[], description="List of comments scraped for this post")
