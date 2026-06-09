from typing import List, Optional
from sqlalchemy import String, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, IDMixin, TimestampMixin


class Page(Base, IDMixin, TimestampMixin):
    """SQLAlchemy model representing a LinkedIn Company Page."""
    
    __tablename__ = "pages"

    # page_id is the unique slug from the URL (e.g. "deepsolv")
    page_id: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    linkedin_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    profile_pic_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    follower_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0", 
        nullable=False, 
        index=True
    )
    head_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0", 
        nullable=False
    )
    
    # Store lists as MySQL native JSON
    specialities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    founded: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="page",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    employees: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="page",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
