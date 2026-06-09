from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    total_pages: int
    results: List[T]


class HealthCheckResponse(BaseModel):
    status: str
    database: str
    version: str
