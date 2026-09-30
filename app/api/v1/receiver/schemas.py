from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from app.models.receiver import EntidadesEnum

class TitleDto(BaseModel):
    abbreviation: str = Field(..., max_length=60)
    meaning: str = Field(...,min_length=3, max_length=150) # Significado

class JobDto(BaseModel):
    abbreviation: str
    meaning: str

class OrganizationDto(BaseModel):
    name: str = Field(..., max_length=200)
    state: str = Field(..., max_length=60)

class PositionDto(BaseModel):
    job_role: JobDto
    organization: OrganizationDto

class AddressDto(BaseModel):
    street: str
    num_street: str
    colony: str
    state: str
    postal_code: str
    city: str
    country: str
    address_reference: Optional[str]

class ContactDto(BaseModel):
    phone: str = Field(...)
    ext: str

class VolanteDto(BaseModel):
    name: str = Field(..., max_length=50)

class ReceiverDto(BaseModel):
    id: int = Field(...)
    type_entity: EntidadesEnum
    title: Optional[str] = TitleDto
    full_name: Optional[str]
    email: Optional[EmailStr]
    position: Optional[PositionDto] = Field(default_factory=list)
    addresses: List[AddressDto] = Field(default_factory=list)
    contacts: Optional[List[ContactDto]] = Field(default_factory=list)
    volantes: Optional[List[VolanteDto]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ReceiverCreate(BaseModel):
    type_entity: EntidadesEnum
    title: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr]
    position: Optional[PositionDto]
    addresses: List[AddressDto]
    contacts: Optional[List[ContactDto]]

class ReceiverUpdate(BaseModel):
    type_entity: Optional[EntidadesEnum]
    title: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    position: Optional[PositionDto]
    addresses: List[AddressDto] = Field(default_factory=list)
    contacts: Optional[List[ContactDto]] = Field(default_factory=list)
    volantes: Optional[List[VolanteDto]] = Field(default_factory=list)