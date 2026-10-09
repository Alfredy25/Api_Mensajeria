from abc import ABC, abstractmethod

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import JobRoleORM


class JobRoleRepository(ABC):
    @abstractmethod
    def find_by_abbreviation(self, abbreviation: str) -> JobRoleORM | None:
        ...

    @abstractmethod
    def create(self, abbreviation: str, meaning: str) -> JobRoleORM:
        ...

    @abstractmethod
    def get_by_id(self, job_id: int) -> JobRoleORM | None:
        ...

    @abstractmethod
    def update(self, job: JobRoleORM, updates: dict) -> JobRoleORM:
        ...

class JobRepositoryImpl(JobRoleRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_abbreviation(self, abbreviation: str) -> JobRoleORM | None:
        return self._db.execute(
            select(JobRoleORM).where(
                JobRoleORM.abbreviation == func.upper(abbreviation)
            )
        ).scalar_one_or_none()

    def create(self, abbreviation: str, meaning: str) -> JobRoleORM:
        job_orm = JobRoleORM(abbreviation=abbreviation, meaning=meaning)
        self._db.add(job_orm)
        self._db.flush()
        return job_orm

    def get_by_id(self, job_id: int) -> JobRoleORM | None:
        return self._db.get(JobRoleORM, job_id)

    def update(self, job: JobRoleORM, updates: dict) -> JobRoleORM:
        for attr, value in updates.items():
            setattr(job, attr, value)
        return job