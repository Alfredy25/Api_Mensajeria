from typing import List, Optional, Self, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.api.v1.address.schemas import AddressCreate, AddressDto
from app.api.v1.contact.schemas import ContactDto, ContactCreate
from app.api.v1.position.schemas import PositionCreateWithReceiver, PositionDto
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
    position: Optional[PositionCreateWithReceiver] = Field(default=None, description="Puesto de la entidad")
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
    full_name: Optional[str] = Field(default=None, min_length=5, max_length=70)
    email: Optional[EmailStr] = Field(default=None, max_length=80)
    title: Optional[TitleCreate] = None
    position: Optional[PositionCreateWithReceiver] = None
    type_entity: Optional[EntidadesEnum] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value: object) -> object:
        if value is None:
            raise ValueError("El nombre no puede ser nulo")
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("title", mode="before")
    @classmethod
    def reject_null_title(cls, value: object) -> object:
        if value is None:
            raise ValueError("El título no puede ser nulo")
        return value

    @field_validator("type_entity", mode="before")
    @classmethod
    def reject_null_type(cls, value: object) -> object:
        if value is None:
            raise ValueError("El tipo no puede ser nulo")
        return value

class PaginatedReceiver(BaseModel):
    page:int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "full_name", "name_org", "created_at"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[ReceiverDto] = Field(default_factory=list)


def normalize_search(value: str) -> str:
    """Recorta espacios y exige al menor 3 caracteres útiles"""
    normalized = value.strip()
    if len(normalized) < 3:
        raise ValueError("Search debe tener al menos 3 caracteres")
    return normalized