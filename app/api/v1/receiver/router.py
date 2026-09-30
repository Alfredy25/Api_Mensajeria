from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import List, Literal

from sqlalchemy.orm import Session

from app.api.v1.receiver.repository import ReceiverRepositoryImpl
from app.api.v1.receiver.schemas import ReceiverDto
from app.core.db import get_db

router = APIRouter(prefix="/receivers", tags=["receivers"])

@router.get("/", response_model=List[ReceiverDto])
def get_receivers(
        type_receiver: Literal["Dependencia", "Persona"] = Query("Persona", description="El tipo de destinatario"),
        name: str = Query(..., examples=["Juan Carlos Garcia"]),
        db: Session = Depends(get_db)
):
    repo = ReceiverRepositoryImpl(db=db)
    if type_receiver == "Persona":
        receivers_orm = repo.find_by_name(full_name=name)
        if not receivers_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existen destinatarios con ese nombre")

        return [ReceiverDto.model_validate(receiver) for receiver in receivers_orm]

    receivers_orm = repo.find_by_dependecy(name=name)
    return receivers_orm


