from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    name: str
    title: Optional[str] = None
    profile_url: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
