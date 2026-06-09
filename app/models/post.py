from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, IDMixin, TimestampMixin


class Post(Base, IDMixin, TimestampMixin):
    __tablename__ = "posts"

    page_id: Mapped[int] = mapped_column(
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    post_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    likes_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    shares_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    
    media_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    media_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    page: Mapped["Page"] = relationship("Page", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
