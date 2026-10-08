from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AddressUpdate(BaseModel):
    street: Optional[str]
    num_street: Optional[str]
    colony: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    country: Optional[str]
    address_reference: Optional[str]

class AddressCreate(BaseModel):
    street: str = Field(..., min_length=3, max_length=80)
    num_street: str = Field(..., min_length=1, max_length=15)
    colony: str = Field(..., min_length=3, max_length=60)
    municipality: str = Field(..., min_length=3, max_length=60)
    city: str = Field(..., min_length=3, max_length=60)
    state: str = Field(..., min_length=3, max_length=50)
    postal_code: str = Field(..., min_length=4, max_length=5)
    country: str = Field(..., min_length=3, max_length=50)
    address_reference: Optional[str] = Field(default=None, max_length=50)


class AddressDto(AddressCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)