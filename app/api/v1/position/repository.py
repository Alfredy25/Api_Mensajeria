from abc import ABC, abstractmethod
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models import PositionORM, JobRoleORM, OrganizationORM


class PositionRepository(ABC):

    @abstractmethod
    def create_position(self, job: JobRoleORM, organization: OrganizationORM) -> PositionORM:
        ...

    @abstractmethod
    def find_position(self, job_id, organization_id) -> PositionORM | None:
        ...

    @abstractmethod
    def get_position_by_id(self, position_id: int) -> PositionORM | None:
        ...


class PositionRepositoryImpl(PositionRepository):

    def __init__(self, db: Session):
        self._db = db

    def create_position(self, job: JobRoleORM, organization: OrganizationORM) -> PositionORM:
        position_orm = PositionORM(job_role=job, organization=organization)
        self._db.add(position_orm)
        self._db.flush()
        return position_orm

    def find_position(self, job_id, organization_id) -> PositionORM | None:
        return self._db.execute(
            select(PositionORM).where(
                and_(
                    PositionORM.job_id == job_id,
                    PositionORM.organization_id == organization_id
                )
            )
        ).scalar_one_or_none()

    def get_position_by_id(self, position_id: int) -> PositionORM | None:
        return self._db.get(PositionORM, position_id)

