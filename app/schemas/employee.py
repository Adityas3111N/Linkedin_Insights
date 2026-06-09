from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    name: str = Field(..., description="Display name of the employee")
    title: Optional[str] = Field(None, description="Job title at the company")
    profile_url: Optional[str] = Field(None, description="LinkedIn profile URL of the employee")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When this record was stored in our database")

    model_config = ConfigDict(from_attributes=True)
