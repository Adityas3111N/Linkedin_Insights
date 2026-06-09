from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, IDMixin, TimestampMixin


class Comment(Base, IDMixin, TimestampMixin):
    __tablename__ = "comments"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_profile_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    commented_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
