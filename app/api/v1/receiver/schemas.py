from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List

from app.api.v1.address.schemas import AddressDto, AddressCreate, AddressUpdate
from app.api.v1.contact.schemas import ContactDto, ContactCreate
from app.api.v1.position.schemas import PositionCreate, PositionDto
from app.api.v1.title.schemas import TitleDto
from app.models.receiver import EntidadesEnum

class VolanteDto(BaseModel):
    id: int
    name: str

class VolanteCreate(BaseModel):
    name: str = Field(..., max_length=50)

class ReceiverDto(BaseModel):
    id: int = Field(...)
    type_entity: EntidadesEnum
    title: Optional[str] = TitleDto
    full_name: Optional[str]
    email: Optional[EmailStr]
    position: Optional[PositionDto]
    addresses: List[AddressDto] = Field(default_factory=list)
    contacts: Optional[List[ContactDto]] = Field(default_factory=list)
    volantes: Optional[List[VolanteDto]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ReceiverCreate(BaseModel):
    type_entity: EntidadesEnum
    title: Optional[TitleDto] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr]
    position: Optional[PositionCreate]
    address: AddressCreate
    contact: Optional[ContactCreate]
    volante: Optional[VolanteCreate]

class ReceiverUpdate(BaseModel):
    type_entity: Optional[EntidadesEnum]
    title: Optional[TitleDto]
    full_name: Optional[str]
    email: Optional[str]