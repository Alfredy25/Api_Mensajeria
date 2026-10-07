from typing import Optional
from pydantic import BaseModel, Field


class ContactDto(BaseModel):
    phone: str = Field(...)
    ext: str | None

class ContactCreate(BaseModel):
    phone: str = Field(..., min_length=8, max_length=10)
    ext: Optional[str] = Field(default=None, max_length=8)

class ContactUpdate(BaseModel):
    phone: Optional[str] = Field(default=None)
    ext: Optional[str] = Field(default=None)