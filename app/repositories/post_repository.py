from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.post import Post


class PostRepository:
    """Encapsulates database operations for the Post entity."""

    def find_by_id(self, db: Session, post_id: int) -> Post | None:
        """Fetch a single post by its primary key ID."""
        return db.get(Post, post_id)

    def find_all_by_page_id(
        self, db: Session, page_id: int, skip: int, limit: int, sort: str = "latest"
    ) -> Tuple[int, List[Post]]:
        """Fetch a paginated list of posts for a specific page."""
        query = select(Post).where(Post.page_id == page_id)
        if sort == "top":
            query = query.order_by(Post.likes_count.desc(), Post.posted_at.desc())
        else:
            query = query.order_by(Post.posted_at.desc())

        # Total posts count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = db.execute(count_query).scalar_one()

        # Paginated results
        query = query.offset(skip).limit(limit)
        results = db.execute(query).scalars().all()

        return total_count, list(results)

    def create(self, db: Session, post_data: dict) -> Post:
        """Insert a single post."""
        post = Post(**post_data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def bulk_create(self, db: Session, posts_data: List[dict]) -> List[Post]:
        """Perform a batch insert of Post dictionaries for efficiency."""
        posts = [Post(**data) for data in posts_data]
        db.add_all(posts)
        db.commit()
        for post in posts:
            db.refresh(post)
        return posts
