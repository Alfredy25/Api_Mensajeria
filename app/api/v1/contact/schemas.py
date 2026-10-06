from typing import Optional
from pydantic import BaseModel, Field


class ContactDto(BaseModel):
    phone: str = Field(...)
    ext: str | None

class ContactCreate(BaseModel):
    phone: str = Field(...)
    ext: Optional[str] = Field(default=None)

class ContactUpdate(BaseModel):
    phone: Optional[str] = Field(default=None)
    ext: Optional[str] = Field(default=None)