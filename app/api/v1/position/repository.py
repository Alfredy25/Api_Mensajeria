from abc import ABC, abstractmethod


from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from app.models import PositionORM, JobRoleORM, OrganizationORM


class PositionRepository(ABC):

    @abstractmethod
    def ensure_cargo(self, abreviatura: str, significado: str) -> JobRoleORM:
        ...

    @abstractmethod
    def ensure_organization(self, name: str, state: str) -> OrganizationORM:
        ...

    @abstractmethod
    def get_position_by_id(self, position_id: int) -> PositionORM:
        ...

    @abstractmethod
    def get_or_create_position(self, job: JobRoleORM,
                               organization: OrganizationORM) -> PositionORM:
        ...

class PositionRepositoryImpl(PositionRepository):

    def __init__(self, db: Session):
        self._db = db

    def ensure_cargo(self, abreviatura: str, significado: str) -> JobRoleORM:
        cargo_obj = self._db.execute(
            select(JobRoleORM).where(
                JobRoleORM.abreviatura == func.upper(abreviatura)
            )
        ).scalar_one_or_none()
        if cargo_obj:
            return cargo_obj

        cargo_obj = JobRoleORM(abreviatura=abreviatura, significado=significado)
        self._db.add(cargo_obj)
        self._db.flush()
        return cargo_obj

    def ensure_organization(self, name: str, state: str) -> OrganizationORM:
        organization_obj = self._db.execute(
            select(OrganizationORM).where(
                and_(
                    OrganizationORM.name == name,
                    OrganizationORM.state == state
                )
            )
        ).scalar_one_or_none()

        if organization_obj:
            return organization_obj

        organization_obj = OrganizationORM(name=name, state=state)
        self._db.add(organization_obj)
        self._db.flush()
        return organization_obj


    def get_or_create_position(self, job: JobRoleORM,
                               organization: OrganizationORM)-> PositionORM:
        position_orm = self._db.execute(
            select(PositionORM).where(
                and_(
                    PositionORM.job_id == job.id,
                    PositionORM.organization_id == organization.id
                )
            )
        ).scalar_one_or_none()
        if position_orm:
            return position_orm

        position_orm = PositionORM(job_role=job, organization=organization)
        self._db.add(position_orm)
        self._db.flush()
        return position_orm

    def get_position_by_id(self, position_id: int) -> PositionORM | None:
        return self._db.get(PositionORM, position_id)

