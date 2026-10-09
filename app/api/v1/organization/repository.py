from abc import ABC, abstractmethod
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from app.models import OrganizationORM


class OrganizationRepository(ABC):

    @abstractmethod
    def find_organization(self, name: str, state: str) -> OrganizationORM:
        ...

    @abstractmethod
    def create_organization(self, name: str, state: str) -> OrganizationORM:
        ...

    @abstractmethod
    def find_by_id(self, organization_id: int) -> OrganizationORM | None:
        ...

    @abstractmethod
    def update(self, org: OrganizationORM, updates: dict) -> OrganizationORM:
        ...

class OrganizationRepositoryImpl(OrganizationRepository):
    def __init__(self, db: Session):
        self._db = db

    def find_organization(self, name: str, state: str) -> OrganizationORM:
        return self._db.execute(
            select(OrganizationORM).where(
                and_(
                    func.upper(OrganizationORM.name) == func.upper(name),
                    func.upper(OrganizationORM.state) == func.upper(state)
                )
            )
        ).scalar_one_or_none()

    def create_organization(self, name: str, state: str) -> OrganizationORM:
        organization_obj = OrganizationORM(name=name, state=state)
        self._db.add(organization_obj)
        self._db.flush()
        return organization_obj

    def find_by_id(self, organization_id: int) -> OrganizationORM | None:
        return self._db.get(OrganizationORM, organization_id)

    def update(self, org: OrganizationORM, updates: dict) -> OrganizationORM:
        for attr, value in updates.items():
            setattr(org, attr, value)
        return org