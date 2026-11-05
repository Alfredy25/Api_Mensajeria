from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import AfterValidator

from app.api.v1.address.schemas import (
    AddressCreate,
    AddressDto,
    AddressUpdate,
    MexicanStateField,
    PaginatedAddresses,
)
from app.api.v1.address.service import AddressService
from app.core.dependencies import get_address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])


def normalize_address_search(value: str) -> str:
    normalized = value.strip()
    if len(normalized) < 2:
        raise ValueError("Search debe tener al menos 2 caracteres")
    return normalized


@router.get("/", response_model=PaginatedAddresses)
def list_addresses(
    search: Optional[
        Annotated[
            str,
            Query(
                default=None,
                min_length=2,
                max_length=50,
                description="Texto para buscar por colonia, calle, ciudad o municipio",
                examples=["Centro", "Reforma", "Guadalajara"],
            ),
            AfterValidator(normalize_address_search),
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
        default=10,
        ge=3,
        le=50,
        description="Cantidad de domicilios (3-50)",
    ),
    order_by: Literal["id", "state"] = Query(
        default="id",
        description="Campo de orden",
    ),
    direction: Literal["desc", "asc"] = Query(
        default="asc",
        description="Dirección del orden",
    ),
    service: AddressService = Depends(get_address_service),
) -> PaginatedAddresses:
    return service.list_addresses(
        search=search,
        state=state,
        page=page,
        page_size=page_size,
        order_by=order_by,
        direction=direction,
    )


@router.post("/{receiver_id}", response_model=AddressDto,status_code=status.HTTP_201_CREATED)
def create_address(
    receiver_id: int = Path(
        ...,
        ge=1,
        description="Identificador del destinatario que ya existe",
        examples=[1],
    ),
    address: AddressCreate = Body(..., description="Domicilio a crear"),
    service: AddressService = Depends(get_address_service),
) -> AddressDto:
    return service.create_address(
        receiver_id=receiver_id,
        address_create=address,
    )


@router.patch("/{address_id}", response_model=AddressDto)
def update_address(
    address_id: int = Path(
        ...,
        ge=1,
        description="Identificador del domicilio a actualizar",
        examples=[1],
    ),
    address: AddressUpdate = Body(
        ...,
        description="Campos del domicilio a actualizar",
    ),
    service: AddressService = Depends(get_address_service),
) -> AddressDto:
    return service.update_address(
        address_update=address,
        address_id=address_id,
    )
