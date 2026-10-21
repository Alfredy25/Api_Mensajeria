from typing import Optional, Literal

from fastapi import APIRouter, Depends, status, Query

from app.api.v1.receiver.schemas import ReceiverDto, ReceiverCreate, PaginatedReceiver
from app.api.v1.receiver.service import ReceiverService
from app.core.dependencies import get_receiver_service

router = APIRouter(prefix="/receivers", tags=["receivers"])


@router.post("/", response_model=ReceiverDto,
             status_code=status.HTTP_201_CREATED,summary="Crear destinatario")
def create_receiver(payload: ReceiverCreate,
                    service: ReceiverService = Depends(get_receiver_service)) -> ReceiverDto:
    """Crea un destinatario con su dirección, contacto y volante opcionales."""
    return service.create_receiver(payload)

@router.get("/", response_model= PaginatedReceiver)
def list_receivers(
        query: Optional[str] = Query(
            default=None,
            description="Texto para buscar por fullname y name de organization",
            alias="search",
            min_length=3, max_length=40,
            pattern=r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", # Desde el inicio de la cadena (^) hasta el final ($), solo se permiten letras mayúsculas, minúsculas, vocales acentuadas, ñ, ü y espacios. Debe existir al menos un carácter (+).
            ),
        page_size: int = Query(
            default=50, ge=5, le=100,
            description="Numero de resultados (10-50)"),
        page: int = Query(
            default=1,
            ge=1, # Desde el inicio de la cadena (^) hasta el final ($), solo se permiten letras mayúsculas, minúsculas, vocales acentuadas, ñ, ü y espacios. Debe existir al menos un carácter (+).gt=1,
            description="Número de página (>=1)"),
        order_by: Literal["id","full_name", "state", "name_org"] = Query(
            default="id",
            description="Campo de orden"),
        direction: Literal["desc", "asc"] = Query(
            default="asc",
            description="direccion del orden"),
        type_entity: Optional[Literal["PERSONA", "GOBIERNO", "PRIVADA"]] = Query(
            default=None,
            description="Tipo de entidad a buscar"),
        state: Optional[str] = Query(
            default=None,
            description="Estado de la republica mexicana para address y estado de la organizacion"),
        service: ReceiverService = Depends(get_receiver_service)
) -> PaginatedReceiver:
    return service.list_receivers(
        query=query,
        page_size=page_size,
        page=page,
        order_by=order_by,
        direction=direction,
        type_entity=type_entity,
        state=state,
    )
