from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def strip_phone(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    return value


def strip_ext(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


class ContactDto(BaseModel):
    id: int
    phone: str = Field(...)
    ext: Optional[str] = None
    id_destinatario: int

    model_config = ConfigDict(from_attributes=True)


class ContactCreate(BaseModel):
    phone: str = Field(..., min_length=8, max_length=10, pattern="^[0-9]+$")
    ext: Optional[str] = Field(default=None, max_length=5, pattern="^[0-9]+$")

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        return strip_phone(value)

    @field_validator("ext", mode="before")
    @classmethod
    def normalize_ext(cls, value: object) -> object:
        return strip_ext(value)


class ContactUpdate(BaseModel):
    phone: Optional[str] = Field(default=None, min_length=8, max_length=10)
    ext: Optional[str] = Field(default=None, max_length=5)

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        if value is None:
            raise ValueError("El teléfono no puede ser nulo")
        return strip_phone(value)

    @field_validator("ext", mode="before")
    @classmethod
    def normalize_ext(cls, value: object) -> object:
        return strip_ext(value)


class PaginatedContacts(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "phone"]
    direction: Literal["desc", "asc"]
    search: Optional[str] = None
    items: List[ContactDto] = Field(default_factory=list)


class TotalsContacts(BaseModel):
    total: int
    total_pages: int
    current_page: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
