from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_abbreviation(value: object) -> object:
    if isinstance(value, str):
        return value.strip().upper()
    return value


def normalize_meaning(value: object) -> object:
    if isinstance(value, str):
        return value.strip().title()
    return value


class JobDto(BaseModel):
    id: int
    abbreviation: str
    meaning: str

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    abbreviation: str = Field(
        ...,
        min_length=2,
        max_length=60,
        examples=["DIR."],
        description="Abreviatura del cargo",
        pattern=r"^[A-Za-zñÑ. ]+$",
    )
    meaning: str = Field(
        ...,
        min_length=3,
        max_length=150,
        examples=["Director"],
        description="Significado de la abreviatura",
        pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$",
    )

    @field_validator("abbreviation", mode="before")
    @classmethod
    def normalize_abbreviation_field(cls, value: object) -> object:
        return normalize_abbreviation(value)

    @field_validator("meaning", mode="before")
    @classmethod
    def normalize_meaning_field(cls, value: object) -> object:
        return normalize_meaning(value)


class JobUpdate(BaseModel):
    abbreviation: Optional[str] = Field(default=None, min_length=2, max_length=60, pattern=r"^[A-Za-zñÑ. ]+$",)
    meaning: Optional[str] = Field(default=None, min_length=3, max_length=150, pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$",)

    @field_validator("abbreviation", mode="before")
    @classmethod
    def normalize_abbreviation_field(cls, value: object) -> object:
        if value is None:
            raise ValueError("La abreviatura no puede ser nula")
        return normalize_abbreviation(value)

    @field_validator("meaning", mode="before")
    @classmethod
    def normalize_meaning_field(cls, value: object) -> object:
        if value is None:
            raise ValueError("El significado no puede ser nulo")
        return normalize_meaning(value)


class PaginatedJobs(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "abbreviation", "meaning"]
    direction: Literal["desc", "asc"]
    search: Optional[str] = None
    items: List[JobDto] = Field(default_factory=list)


class TotalsJobs(BaseModel):
    total: int
    total_pages: int
    current_page: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
