from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import AfterValidator

from app.api.v1.address.schemas import MexicanStateField
from app.api.v1.organization.schemas import (
    OrganizationCreate,
    OrganizationDto,
    OrganizationUpdate,
    PaginatedOrganizations,
)
from app.api.v1.organization.service import OrganizationService
from app.api.v1.receiver.schemas import normalize_search
from app.core.dependencies import get_organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=PaginatedOrganizations)
def list_organizations(
    search: Optional[
        Annotated[
            str,
            Query(
                default=None,
                min_length=3,
                max_length=180,
                pattern=r"^[a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ.\s]+$",
                description="Texto para buscar por nombre",
                examples=["CONGRESO", "Auditoría"],
            ),
            AfterValidator(normalize_search),
        ]
    ] = None,
    state: Optional[MexicanStateField] = Query(
        default=None,
        description="Estado de la republica mexicana",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Número de página (>=1)",
    ),
    page_size: int = Query(
        default=50,
        ge=5,
        le=80,
        description="Cantidad de organizaciones (5-80)",
    ),
    order_by: Literal["id", "name", "state"] = Query(
        default="id",
        description="Campo de orden",
    ),
    direction: Literal["desc", "asc"] = Query(
        default="asc",
        description="Dirección del orden",
    ),
    service: OrganizationService = Depends(get_organization_service),
) -> PaginatedOrganizations:
    return service.list_organizations(
        search=search,
        state=state,
        page=page,
        page_size=page_size,
        order_by=order_by,
        direction=direction,
    )


@router.post(
    "/",
    response_model=OrganizationDto,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    organization: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDto:
    return service.create_organization(organization)


@router.patch("/{organization_id}", response_model=OrganizationDto)
def update_organization(
    organization_id: int = Path(
        ...,
        ge=1,
        description="Identificador de la organización a actualizar",
        examples=[1],
    ),
    organization: OrganizationUpdate = Body(
        ...,
        description="Campos de la organización a actualizar",
    ),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDto:
    return service.update_organization(
        organization_id=organization_id,
        organization=organization,
    )
