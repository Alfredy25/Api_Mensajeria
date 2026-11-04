from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import AfterValidator

from app.api.v1.contact.schemas import (
    ContactCreate,
    ContactDto,
    ContactUpdate,
    PaginatedContacts,
)
from app.api.v1.contact.service import ContactService
from app.core.dependencies import get_contact_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


def normalize_contact_search(value: str) -> str:
    normalized = value.strip()
    if len(normalized) < 2:
        raise ValueError("Search debe tener al menos 2 caracteres")
    return normalized


@router.get("/", response_model=PaginatedContacts)
def list_contacts(
    search: Optional[
        Annotated[
            str,
            Query(
                default=None,
                min_length=2,
                max_length=10,
                description="Fragmento de teléfono para buscar",
                examples=["8444160470", "8444"],
            ),
            AfterValidator(normalize_contact_search),
        ]
    ] = None,
    page: int = Query(
        default=1,
        ge=1,
        description="Número de página (>=1)",
    ),
    page_size: int = Query(
        default=10,
        ge=3,
        le=50,
        description="Cantidad de contactos (3-50)",
    ),
    order_by: Literal["id", "phone"] = Query(
        default="id",
        description="Campo de orden",
    ),
    direction: Literal["desc", "asc"] = Query(
        default="asc",
        description="Dirección del orden",
    ),
    service: ContactService = Depends(get_contact_service),
) -> PaginatedContacts:
    return service.list_contacts(
        search=search,
        page=page,
        page_size=page_size,
        order_by=order_by,
        direction=direction,
    )


@router.post(
    "/{receiver_id}",
    response_model=ContactDto,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    receiver_id: int = Path(
        ...,
        ge=1,
        description="Identificador del destinatario que ya existe",
        examples=[1],
    ),
    contact: ContactCreate = Body(..., description="Contacto a crear"),
    service: ContactService = Depends(get_contact_service),
) -> ContactDto:
    return service.create_contact(
        receiver_id=receiver_id,
        contact=contact,
    )


@router.patch("/{contact_id}", response_model=ContactDto)
def update_contact(
    contact_id: int = Path(
        ...,
        ge=1,
        description="Identificador del contacto a actualizar",
        examples=[1],
    ),
    contact: ContactUpdate = Body(
        ...,
        description="Campos del contacto a actualizar",
    ),
    service: ContactService = Depends(get_contact_service),
) -> ContactDto:
    return service.update_contact(
        contact_id=contact_id,
        contact=contact,
    )
