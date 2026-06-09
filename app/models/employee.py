from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, IDMixin, TimestampMixin


class Employee(Base, IDMixin, TimestampMixin):
    """SQLAlchemy model representing an Employee of a LinkedIn Company."""
    
    __tablename__ = "employees"

    # Foreign key referencing pages.id
    page_id: Mapped[int] = mapped_column(
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    page: Mapped["Page"] = relationship("Page", back_populates="employees")
