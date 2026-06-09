from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

connect_args = {}
# Auto-enable SSL for cloud databases (like Aiven) to avoid driver connection errors
if "aivencloud.com" in settings.DATABASE_URL or "ssl-mode=" in settings.DATABASE_URL:
    connect_args["ssl"] = {}
    # Remove query params that PyMySQL doesn't support natively
    if "?" in settings.DATABASE_URL:
        db_url = settings.DATABASE_URL.split("?")[0]
    else:
        db_url = settings.DATABASE_URL
else:
    db_url = settings.DATABASE_URL

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.APP_DEBUG
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
