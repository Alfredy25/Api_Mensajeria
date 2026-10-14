from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ContactDto(BaseModel):
    id: int
    phone: str = Field(...)
    ext: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContactCreate(BaseModel):
    phone: str = Field(..., min_length=8, max_length=10)
    ext: Optional[str] = Field(default=None, max_length=5)

class ContactUpdate(BaseModel):
    phone: Optional[str] = Field(default=None)
    ext: Optional[str] = Field(default=None)