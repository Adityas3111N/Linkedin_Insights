from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized response format for paginated collections."""
    
    total: int = Field(..., description="Total number of items available")
    page: int = Field(..., description="Current page number (1-indexed)")
    size: int = Field(..., description="Number of items returned in this page")
    total_pages: int = Field(..., description="Total number of pages available")
    results: List[T] = Field(..., description="The list of items on the current page")


class HealthCheckResponse(BaseModel):
    """Standard response format for the application health check endpoint."""
    
    status: str = Field(..., description="Overall health status")
    database: str = Field(..., description="Database connection status")
    version: str = Field(..., description="Application version")
