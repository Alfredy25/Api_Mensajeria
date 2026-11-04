from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.job_role.repository import JobRoleRepository
from app.api.v1.job_role.schemas import JobCreate, JobDto, JobUpdate, PaginatedJobs
from app.models import JobRoleORM


class JobService:
    def __init__(self, db: Session, repo: JobRoleRepository):
        self._db = db
        self._repo = repo

    def create_job(self, job: JobCreate) -> JobDto:
        existing = self._repo.find_by_abbreviation(job.abbreviation)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El cargo ya existe",
            )
        try:
            job_orm_new = self._repo.create(
                abbreviation=job.abbreviation,
                meaning=job.meaning,
            )
            self._db.commit()
            self._db.refresh(job_orm_new)
            return JobDto.model_validate(job_orm_new, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def get_jobs(
        self,
        search: str | None,
        page: int,
        limit: int,
        order_by: Literal["id", "abbreviation", "meaning"],
        direction: Literal["desc", "asc"],
    ) -> PaginatedJobs:
        totals, jobs = self._repo.get_jobs(
            search=search.strip().upper() if search else None,
            page=page,
            limit=limit,
            order_by=order_by,
            direction=direction,
        )
        current_page = totals.current_page
        total = totals.total
        total_pages = totals.total_pages

        has_prev = current_page > 1 and total > 0
        has_next = current_page < total_pages if total_pages > 0 else False

        return PaginatedJobs(
            page=current_page,
            page_size=limit,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            order_by=order_by,
            direction=direction,
            search=search,
            items=[
                JobDto.model_validate(job, from_attributes=True)
                for job in jobs
            ],
        )

    def update_job(self, job_id: int, job: JobUpdate) -> JobDto:
        job_orm = self._repo.get_by_id(job_id=job_id)
        if job_orm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cargo con id {job_id} no existe",
            )
        updates = job.model_dump(exclude_unset=True)
        self._reject_abbreviation_of_another(job_orm, updates)
        try:
            job_orm_update = self._repo.update(job_orm, updates=updates)
            self._db.commit()
            self._db.refresh(job_orm_update)
            return JobDto.model_validate(job_orm_update, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def _reject_abbreviation_of_another(
        self,
        current: JobRoleORM,
        updates: dict,
    ) -> None:
        abbreviation = updates.get("abbreviation")
        if abbreviation is None:
            return

        owner = self._repo.find_by_abbreviation(abbreviation)
        if owner is None: 
            return
        
        if owner.id != current.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El cargo ya existe",
            )

    def ensure_job_role(self, job: JobCreate) -> JobRoleORM:
        job_orm = self._repo.find_by_abbreviation(job.abbreviation)
        if job_orm:
            return job_orm
        job_orm_new = self._repo.create(
            abbreviation=job.abbreviation,
            meaning=job.meaning,
        )
        return job_orm_new

    def get_job(self, job_id: int) -> JobDto:
        job_orm = self._repo.get_by_id(job_id=job_id)
        return JobDto.model_validate(job_orm, from_attributes=True)