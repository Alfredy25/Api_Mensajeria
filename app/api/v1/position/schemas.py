from typing import Optional

from pydantic import BaseModel, Field


class JobDto(BaseModel):
    id: int
    abbreviation: str
    meaning: str

class JobCreate(BaseModel):
    abbreviation: str
    meaning: str

class OrganizationDto(BaseModel):
    id: int
    name: str
    state: str

class OrganizationCreate(BaseModel):
    name: str = Field(..., max_length=200)
    state: str = Field(..., max_length=60)

class PositionDto(BaseModel):
    id: int
    job_role: JobDto
    organization: OrganizationDto

class PositionCreate(BaseModel):
    job_role: JobCreate
    organization: OrganizationCreate

class JobUpdate(BaseModel):
    abbreviation: Optional[str]
    meaning: Optional[str]

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    state: Optional[str]

class PositionUpdate(BaseModel):
    job_role: Optional[JobUpdate]
    organization: Optional[OrganizationUpdate]