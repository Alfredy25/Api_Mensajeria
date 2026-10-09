from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.organization.repository import OrganizationRepository
from app.api.v1.organization.schemas import OrganizationCreate, OrganizationDto, OrganizationUpdate
from app.models import OrganizationORM


class OrganizationService:

    def __init__(self, db: Session, repo: OrganizationRepository):
        self._db = db
        self._repo = repo

    def create_organization(self, organization: OrganizationCreate) -> OrganizationDto:
        organization_orm = self._repo.find_organization(name=organization.name, state=organization.state)
        if organization_orm:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization already exists")
        try:
            organization_orm = self._repo.create_organization(name=organization.name, state=organization.state)
            self._db.commit()
            self._db.refresh(organization_orm)
            return OrganizationDto.model_validate(organization_orm, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def update_organization(self, org_id: int, organization: OrganizationUpdate) -> OrganizationDto:
        organization_orm = self._repo.find_by_id(organization_id=org_id)
        if not organization_orm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        updates = organization.model_dump(exclude_unset=True)
        try:
            organization_orm_update = self._repo.update(org=organization_orm, updates=updates)
            self._db.commit()
            self._db.refresh(organization_orm_update)
            return OrganizationDto.model_validate(organization_orm_update, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def ensure_organization(self, org_create: OrganizationCreate) -> OrganizationORM:
        org_orm = self._repo.find_organization(name=org_create.name, state=org_create.state)
        if org_orm:
            return org_orm

        org_orm = self._repo.create_organization(name=org_create.name, state=org_create.state)
        return org_orm



