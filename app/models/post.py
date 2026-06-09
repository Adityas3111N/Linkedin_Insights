from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, IDMixin, TimestampMixin


class Post(Base, IDMixin, TimestampMixin):
    """SQLAlchemy model representing a LinkedIn Post made by a Page."""
    
    __tablename__ = "posts"

    # Foreign key referencing pages.id
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
    media_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "image", "video", "article", "none"
    
    # Timestamp of when it was published on LinkedIn (might differ from created_at insertion timestamp)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    page: Mapped["Page"] = relationship("Page", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
