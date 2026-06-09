from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.comment import Comment


class CommentRepository:
    """Encapsulates database operations for the Comment entity."""

    def find_all_by_post_id(
        self, db: Session, post_id: int, skip: int, limit: int
    ) -> Tuple[int, List[Comment]]:
        """Fetch a paginated list of comments for a specific post."""
        query = select(Comment).where(Comment.post_id == post_id).order_by(Comment.commented_at.asc())

        # Count total comments
        count_query = select(func.count()).select_from(query.subquery())
        total_count = db.execute(count_query).scalar_one()

        # Paginated items
        query = query.offset(skip).limit(limit)
        results = db.execute(query).scalars().all()

        return total_count, list(results)

    def bulk_create(self, db: Session, comments_data: List[dict]) -> List[Comment]:
        """Perform a batch insert of Comment dictionaries."""
        comments = [Comment(**data) for data in comments_data]
        db.add_all(comments)
        db.commit()
        for comment in comments:
            db.refresh(comment)
        return comments
