
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.job_role.repository import JobRoleRepository
from app.api.v1.job_role.schemas import JobCreate, JobDto, JobUpdate
from app.models import JobRoleORM


class JobService:
    def __init__(self, db: Session, repo: JobRoleRepository):
        self._db = db
        self._repo = repo

    def create_job(self, job: JobCreate) -> JobDto:
        job_orm = self._repo.find_by_abbreviation(job.abbreviation)
        if job_orm is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job with abbreviation already exists")
        try:
            job_orm_new = self._repo.create(abbreviation=job.abbreviation,meaning=job.meaning)
            self._db.commit()
            self._db.refresh(job_orm_new)
            return JobDto.model_validate(job_orm_new, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def update_job(self, job_id: int, job: JobUpdate):
        job_orm = self._repo.get_by_id(job_id=job_id)
        if job_orm is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
        updates = job.model_dump(exclude_unset=True)
        job_orm_update = self._repo.update(job_orm, updates=updates)
        self._db.commit()
        return JobDto.model_validate(job_orm_update, from_attributes=True)

    def ensure_job_role(self, job: JobCreate) -> JobRoleORM:
        job_orm = self._repo.find_by_abbreviation(job.abbreviation)
        if job_orm:
            return job_orm
        job_orm_new = self._repo.create(abbreviation=job.abbreviation, meaning=job.meaning)
        return job_orm_new



