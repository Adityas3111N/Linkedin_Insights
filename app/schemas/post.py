from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.comment import CommentResponse


class PostBase(BaseModel):
    content: Optional[str] = None
    post_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    posted_at: Optional[datetime] = None


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostResponse):
    comments: List[CommentResponse] = []
