from fastapi import APIRouter, Depends, status

from app.api.v1.receiver.schemas import ReceiverDto, ReceiverCreate
from app.api.v1.receiver.service import ReceiverService
from app.core.dependencies import get_receiver_service

router = APIRouter(prefix="/receivers", tags=["receivers"])


@router.post("/", response_model=ReceiverDto,
             status_code=status.HTTP_201_CREATED,summary="Crear destinatario")
def create_receiver(payload: ReceiverCreate,
                    service: ReceiverService = Depends(get_receiver_service)) -> ReceiverDto:
    """Crea un destinatario con su dirección, contacto y volante opcionales."""
    return service.create_receiver(payload)
