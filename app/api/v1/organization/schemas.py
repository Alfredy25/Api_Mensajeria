from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=180)
    state: str = Field(..., max_length=60)

class OrganizationDto(BaseModel):
    id: int
    name: str
    state: str

    model_config = ConfigDict(from_attributes=True)