from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import HealthCheckResponse

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        
    status = "healthy" if db_status == "connected" else "unhealthy"
    
    return HealthCheckResponse(
        status=status,
        database=db_status,
        version="1.0.0"
    )
