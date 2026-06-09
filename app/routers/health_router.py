from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import HealthCheckResponse

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """Check application health and verify database connectivity."""
    db_status = "connected"
    
    try:
        # Execute a simple query to confirm database responsiveness
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        
    overall_status = "healthy" if db_status == "connected" else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        version="1.0.0"
    )
