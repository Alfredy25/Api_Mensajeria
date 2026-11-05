from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.address.schemas import MexicanState
from app.api.v1.organization.repository import OrganizationRepository
from app.api.v1.organization.schemas import (
    OrganizationCreate,
    OrganizationDto,
    OrganizationUpdate,
    PaginatedOrganizations,
)
from app.models import OrganizationORM


class OrganizationService:

    def __init__(self, db: Session, repo: OrganizationRepository):
        self._db = db
        self._repo = repo

    def create_organization(
        self,
        organization: OrganizationCreate,
    ) -> OrganizationDto:
        existing = self._repo.find_organization(
            name=organization.name,
            state=organization.state,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La organización ya existe",
            )

        created = self._repo.create_organization(
            name=organization.name,
            state=organization.state,
        )
        return self._commit(created)

    def list_organizations(
        self,
        search: str | None,
        state: MexicanState | None,
        page: int,
        page_size: int,
        order_by: Literal["id", "name", "state"],
        direction: Literal["asc", "desc"],
    ) -> PaginatedOrganizations:
        normalized_search = search.strip().upper() if search else None
        normalized_state = state.value if state else None

        totals, organizations = self._repo.get_organizations(
            search=normalized_search,
            state=normalized_state,
            page=page,
            page_size=page_size,
            order_by=order_by,
            direction=direction,
        )

        current_page = totals.current_page
        total = totals.total
        total_pages = totals.total_pages
        has_prev = current_page > 1 and total > 0
        has_next = total_pages > 0 and current_page < total_pages

        return PaginatedOrganizations(
            page=current_page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            order_by=order_by,
            direction=direction,
            search=search,
            state=state,
            items=[
                OrganizationDto.model_validate(organization)
                for organization in organizations
            ],
        )

    def update_organization(
        self,
        organization_id: int,
        organization: OrganizationUpdate,
    ) -> OrganizationDto:
        current = self._find_organization(organization_id)
        updates = organization.model_dump(exclude_unset=True, mode="json")
        self._reject_same_name_in_state(current, updates)

        updated = self._repo.update(current, updates)
        return self._commit(updated)

    def _find_organization(self, organization_id: int) -> OrganizationORM:
        organization = self._repo.find_by_id(organization_id)
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organización con id {organization_id} no existe",
            )
        return organization

    def _reject_same_name_in_state(
        self,
        current: OrganizationORM,
        updates: dict,
    ) -> None:
        name = updates.get("name", current.name)
        state = updates.get("state", current.state)
        owner = self._repo.find_organization(name=name, state=state)
        if owner is None:
            return
        if owner.id == current.id:
            return

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La organización ya existe",
        )

    def _commit(self, organization: OrganizationORM) -> OrganizationDto:
        try:
            self._db.commit()
            self._db.refresh(organization)
            return OrganizationDto.model_validate(organization)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def ensure_organization(
        self,
        org_create: OrganizationCreate,
    ) -> OrganizationORM:
        org_orm = self._repo.find_organization(
            name=org_create.name,
            state=org_create.state,
        )
        if org_orm:
            return org_orm

        return self._repo.create_organization(
            name=org_create.name,
            state=org_create.state,
        )
