
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.job_role.repository import JobRoleRepository
from app.api.v1.organization.repository import OrganizationRepository
from app.api.v1.position.repository import PositionRepository
from app.api.v1.position.schemas import PositionCreate, PositionDto, JobDto, OrganizationDto
from app.models import OrganizationORM, JobRoleORM, PositionORM


class PositionService:

    def __init__(self, db: Session, repo: PositionRepository,
                 repo_job: JobRoleRepository, repo_org: OrganizationRepository):
        self._db = db
        self._repo = repo
        self._repo_job = repo_job
        self._repo_org = repo_org

    def create_position(self, position: PositionCreate) -> PositionDto:
        job_orm = self._repo_job.find_by_abbreviation(
            position.job_role.abbreviation
        )
        if not job_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="job role not found"
            )

        organization_orm = self._repo_org.find_organization(
            name=position.organization.name,
            state=position.organization.state
        )
        if not organization_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="organization not found"
            )

        position_orm = self._repo.find_position(
            job_id=job_orm.id,
            organization_id=organization_orm.id
        )
        if position_orm:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Position already exists"
            )
        try:
            position_orm_new = self._repo.create_position(job=job_orm, organization=organization_orm)
            self._db.commit()
            self._db.refresh(position_orm_new)
            return PositionDto.model_validate(position_orm_new, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def ensure_position(self, job: JobRoleORM,
                               organization: OrganizationORM)-> PositionORM:
        position_orm = self._repo.find_position(
            job_id=job.id, organization_id=organization.id
        )
        if position_orm:
            return position_orm
        position_orm_new = self._repo.create_position(job=job, organization=organization)
        return position_orm_new