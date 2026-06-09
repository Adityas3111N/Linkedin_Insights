from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Create the SQLAlchemy engine using our settings configuration
# pool_pre_ping=True checks connections and reconnects if MySQL drops them
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.APP_DEBUG
)

# Create a sessionmaker factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """Dependency generator that yields a database session.

    Yields:
        Session: A transaction-backed SQLAlchemy session.

    Note:
        FastAPI executes the block after 'yield' once the request terminates,
        ensuring the session is always closed properly even during failures.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
