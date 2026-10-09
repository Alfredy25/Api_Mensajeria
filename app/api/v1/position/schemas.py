from typing import Optional
from pydantic import BaseModel
from app.api.v1.job_role.schemas import JobDto, JobCreate, JobUpdate
from app.api.v1.organization.schemas import OrganizationDto, OrganizationCreate, OrganizationUpdate


class PositionDto(BaseModel):
    id: int
    job_role: JobDto
    organization: OrganizationDto

class PositionCreate(BaseModel):
    job_role: JobCreate
    organization: OrganizationCreate

class PositionCreateWithReceiver(BaseModel):
    job_role: Optional[JobCreate] = None
    organization: OrganizationCreate

class PositionUpdate(BaseModel):
    job_role: Optional[JobUpdate]
    organization: Optional[OrganizationUpdate]