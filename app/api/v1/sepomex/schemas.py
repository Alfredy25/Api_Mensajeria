from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.address.schemas import MexicanState


class SepomexDto(BaseModel):
    """Asentamiento devuelto por la consulta de un código postal."""

    id: int
    postal_code: str = Field(..., min_length=5, max_length=5)
    settlement: str
    settlement_type: str
    municipality: str
    city: Optional[str] = None
    state: MexicanState
    state_code: str
    zone: str

    model_config = ConfigDict(from_attributes=True)
