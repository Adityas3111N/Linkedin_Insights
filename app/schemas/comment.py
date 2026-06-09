from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    author_name: Optional[str] = Field(None, description="Display name of the comment author")
    author_profile_url: Optional[str] = Field(None, description="LinkedIn profile URL of the author")
    text: str = Field(..., description="The content text of the comment")
    commented_at: Optional[datetime] = Field(None, description="When the comment was published on LinkedIn")


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When this comment was stored in our database")

    model_config = ConfigDict(from_attributes=True)
