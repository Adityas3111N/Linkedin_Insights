import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import page_router, health_router
from app.utils.exceptions import PageNotFoundException, ScrapingException, PostNotFoundException

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Remove top-level table initialization to avoid import-time database connection failures.
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LinkedIn Insights Microservice",
    description="Backend API for fetching, caching, and querying LinkedIn Page insights.",
    version="1.0.0",
    debug=settings.APP_DEBUG
)

@app.on_event("startup")
def on_startup():
    """Execute startup events, initializing database tables."""
    logger.info("Initializing database tables on startup...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {str(e)}")

# Add CORS Middleware (crucial for frontend connections)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers to map Domain Exceptions to REST responses
@app.exception_handler(PageNotFoundException)
def handle_page_not_found(request: Request, exc: PageNotFoundException):
    logger.warning(f"Exception intercepted: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(ScrapingException)
def handle_scraping_failed(request: Request, exc: ScrapingException):
    logger.error(f"Exception intercepted: {exc}")
    return JSONResponse(
        status_code=502,
        content={"detail": f"External scraper failure: {exc.reason}"}
    )


@app.exception_handler(PostNotFoundException)
def handle_post_not_found(request: Request, exc: PostNotFoundException):
    logger.warning(f"Exception intercepted: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )



# Attach routers to their designated paths
app.include_router(health_router)
app.include_router(page_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """Service landing redirect description."""
    return {
        "service": "LinkedIn Insights Microservice",
        "documentation": "/docs",
        "status": "active"
    }
