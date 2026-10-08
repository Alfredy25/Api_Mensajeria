from typing import List, Optional, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pydantic_core import PydanticCustomError

from app.api.v1.address.schemas import AddressCreate, AddressDto
from app.api.v1.contact.schemas import ContactDto, ContactCreate
from app.api.v1.position.schemas import PositionCreate, PositionDto
from app.api.v1.title.schemas import TitleDto, TitleCreate
from app.api.v1.volante.schemas import VolanteDto, VolanteCreate
from app.models.receiver import EntidadesEnum

class ReceiverDto(BaseModel):
    id: int = Field(...)
    type_entity: EntidadesEnum = Field(..., description="Tipo de entidad")
    title: Optional[TitleDto] = Field(default=None, description="Título de la persona si es de tipo PERSONA")
    full_name: Optional[str] = Field(default=None, description="Nombre completo de la persona si es de tipo PERSONA")
    email: Optional[EmailStr] = None
    position: Optional[PositionDto] = Field(default=None, description="Puesto de la persona o puesto de entidad")
    addresses: List[AddressDto] = Field(default_factory=list)
    contacts: List[ContactDto] = Field(default_factory=list)
    volantes: List[VolanteDto] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ReceiverCreate(BaseModel):
    type_entity: EntidadesEnum = Field(..., description="Tipo de entidad")
    title: Optional[TitleCreate] = Field(default=None, description="Título de la persona si es de tipo PERSONA")
    full_name: Optional[str] = Field(default=None, min_length=5, max_length=70, description="Nombre completo de la persona si es de tipo PERSONA")
    email: Optional[EmailStr] = Field(default=None, max_length=80, description="Email de la entidad")
    position: Optional[PositionCreate] = Field(default=None, description="Puesto de la entidad")
    address: AddressCreate = Field(..., description="Dirección de la entidad")
    contact: Optional[ContactCreate] = Field(default=None, description="Contacto de la entidad")
    volante: Optional[VolanteCreate] = Field(default=None, description="Volante de la entidad")

    @model_validator(mode='after')
    def validate_by_type(self) -> Self:
        """Válida los campos permitidos según el tipo de destinatario."""
        if self.type_entity == EntidadesEnum.PERSONA:
            if self.full_name is None or not self.full_name.strip():
                raise PydanticCustomError(
                    "receiver_full_name_required_for_persona",
                    "full_name es requerido para PERSONA"
                    )
            if self.title is None:
                raise PydanticCustomError(
                    "receiver_title_required_for_persona",
                    "title es requerido para PERSONA"
                    )
            return self

        if self.full_name is not None or self.title is not None:
            raise PydanticCustomError(
                "receiver_name_title_forbidden_for_government_or_private",
                "full_name y title no son permitidos para GOBIERNO o PRIVADA"
                )
        if self.position is None:
            raise PydanticCustomError(
                "receiver_position_required",
                "El puesto es requerido para GOBIERNO o PRIVADA"
                )
        return self
                

class ReceiverUpdate(BaseModel):
    type_entity: Optional[EntidadesEnum] = None
    title: Optional[TitleDto] = None
    full_name: Optional[str] = None
    email: Optional[str] = None