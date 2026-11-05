from abc import ABC, abstractmethod
from math import ceil

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.api.v1.organization.schemas import TotalsOrganizations
from app.models import OrganizationORM


class OrganizationRepository(ABC):

    @abstractmethod
    def find_organization(self, name: str, state: str) -> OrganizationORM | None:
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

    @abstractmethod
    def get_organizations(
        self,
        search: str | None,
        state: str | None,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsOrganizations, list[OrganizationORM]]:
        ...


class OrganizationRepositoryImpl(OrganizationRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_organization(self, name: str, state: str) -> OrganizationORM | None:
        return self._db.execute(
            select(OrganizationORM).where(
                and_(
                    func.upper(OrganizationORM.name) == func.upper(name),
                    func.upper(OrganizationORM.state) == func.upper(state),
                )
            )
        ).scalar_one_or_none()

    def create_organization(self, name: str, state: str) -> OrganizationORM:
        organization = OrganizationORM(name=name, state=state)
        self._db.add(organization)
        self._db.flush()
        return organization

    def find_by_id(self, organization_id: int) -> OrganizationORM | None:
        return self._db.get(OrganizationORM, organization_id)

    def update(self, org: OrganizationORM, updates: dict) -> OrganizationORM:
        for field_name, value in updates.items():
            setattr(org, field_name, value)
        return org

    def get_organizations(
        self,
        search: str | None,
        state: str | None,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsOrganizations, list[OrganizationORM]]:
        stmt = self._apply_filters(select(OrganizationORM), search, state)
        total = self._count(search, state)
        totals = self._calculate_totals(total, page_size, page)

        stmt = self._apply_order(stmt, order_by, direction)
        organizations = list(
            self._db.scalars(
                stmt.offset(totals.offset).limit(page_size)
            ).all()
        )
        return totals, organizations

    def _count(self, search: str | None, state: str | None) -> int:
        stmt = self._apply_filters(
            select(func.count()).select_from(OrganizationORM),
            search,
            state,
        )
        return self._db.scalar(stmt) or 0

    @staticmethod
    def _apply_filters(
        stmt: Select,
        search: str | None,
        state: str | None,
    ) -> Select:
        if search:
            term = f"%{search}%"
            stmt = stmt.where(func.upper(OrganizationORM.name).like(term))

        if state:
            stmt = stmt.where(OrganizationORM.state == state)

        return stmt

    @staticmethod
    def _calculate_totals(
        total: int,
        page_size: int,
        page: int,
    ) -> TotalsOrganizations:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size

        return TotalsOrganizations(
            total=total,
            total_pages=total_pages,
            current_page=current_page,
            offset=offset,
        )

    @staticmethod
    def _apply_order(stmt: Select, order_by: str, direction: str) -> Select:
        if order_by == "name":
            column = OrganizationORM.name
        elif order_by == "state":
            column = OrganizationORM.state
        else:
            column = OrganizationORM.id

        if direction == "asc":
            return stmt.order_by(column.asc())

        return stmt.order_by(column.desc())
