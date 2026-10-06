from typing import Optional
from pydantic import BaseModel, ConfigDict


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
    street: str
    num_street: str
    colony: str
    state: str
    postal_code: str
    city: str
    country: str
    address_reference: Optional[str]


class AddressDto(AddressCreate):
    address_id: int

    model_config = ConfigDict(from_attributes=True)