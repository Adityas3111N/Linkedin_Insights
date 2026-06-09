from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    author_name: Optional[str] = None
    author_profile_url: Optional[str] = None
    text: str
    commented_at: Optional[datetime] = None


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
