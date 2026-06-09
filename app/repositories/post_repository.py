from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.post import Post


class PostRepository:
    def find_by_id(self, db: Session, post_id: int) -> Post | None:
        return db.get(Post, post_id)

    def find_all_by_page_id(
        self, db: Session, page_id: int, skip: int, limit: int, sort: str = "latest"
    ) -> Tuple[int, List[Post]]:
        query = select(Post).where(Post.page_id == page_id)
        if sort == "top":
            query = query.order_by(Post.likes_count.desc(), Post.posted_at.desc())
        else:
            query = query.order_by(Post.posted_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar_one()

        query = query.offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return total, list(items)

    def create(self, db: Session, data: dict) -> Post:
        post = Post(**data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def bulk_create(self, db: Session, data: List[dict]) -> List[Post]:
        posts = [Post(**d) for d in data]
        db.add_all(posts)
        db.commit()
        for p in posts:
            db.refresh(p)
        return posts
