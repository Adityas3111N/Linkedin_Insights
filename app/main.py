import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import page_router, health_router
from app.utils.exceptions import PageNotFoundException, ScrapingException, PostNotFoundException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LinkedIn Insights Microservice",
    version="1.0.0",
    debug=settings.APP_DEBUG
)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(PageNotFoundException)
def handle_page_not_found(request: Request, exc: PageNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(ScrapingException)
def handle_scraping_failed(request: Request, exc: ScrapingException):
    return JSONResponse(
        status_code=502,
        content={"detail": f"External scraper failure: {exc.reason}"}
    )

@app.exception_handler(PostNotFoundException)
def handle_post_not_found(request: Request, exc: PostNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

app.include_router(health_router)
app.include_router(page_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "service": "LinkedIn Insights API",
        "status": "healthy"
    }
