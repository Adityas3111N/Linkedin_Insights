from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.comment import Comment


class CommentRepository:
    def find_all_by_post_id(
        self, db: Session, post_id: int, skip: int, limit: int
    ) -> Tuple[int, List[Comment]]:
        query = select(Comment).where(Comment.post_id == post_id).order_by(Comment.commented_at.asc())

        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar_one()

        query = query.offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return total, list(items)

    def bulk_create(self, db: Session, data: List[dict]) -> List[Comment]:
        comments = [Comment(**d) for d in data]
        db.add_all(comments)
        db.commit()
        for c in comments:
            db.refresh(c)
        return comments
