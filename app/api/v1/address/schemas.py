from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AddressUpdate(BaseModel):
    street: Optional[str] = None
    num_street: Optional[str] = None
    colony: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address_reference: Optional[str] = None

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