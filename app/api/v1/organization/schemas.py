import re
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.address.schemas import MexicanState, MexicanStateField, replace_special_characters

NAME_ABBREVIATIONS = {
    "UNIVERSIDAD": "UNI.",
    "AUTONOMA": "AUT.",
    "SECRETARIA DE ADMINISTRACION TRIBUTARIA": "S.A.T.",
    "SECRETARIA DE CONTRALORIA GENERAL": "S.C.E.",
    "ORGANO INTERNO DE CONTROL": "O.I.C.",
    "ORGANO DE CONTROL INTERNO": "O.I.C.",
    "CONTRALORIA GENERAL DEL ESTADO": "C.G.E.",
    "BAJA CALIFORNIA SUR": "B.C.S.",
    "SAN LUIS POTOSI": "S.L.P.",
}

def replace_whole_words(value: str) -> str:
    words = sorted(
        NAME_ABBREVIATIONS,
        key=len,
        reverse=True,
    )

    regex = r"\b(?:{})\b".format(
        "|".join(
            re.escape(word)
            for word in words
        )
    )

    pattern = re.compile(regex)

    text = pattern.sub(
        lambda match: NAME_ABBREVIATIONS[match.group(0)],
        value
    )

    return replace_special_characters(text)

def normalize_organization_name(value: object) -> object:
    if isinstance(value, str):
        return replace_whole_words(value.strip().upper())
    return value


class OrganizationDto(BaseModel):
    id: int
    name: str
    state: MexicanStateField

    model_config = ConfigDict(from_attributes=True)


class OrganizationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=180,
        examples=["CONGRESO DEL ESTADO DE TABASCO"],
    )
    state: MexicanStateField = Field(
        ...,
        description="Estado de la republica mexicana",
        examples=["TABASCO"],
    )

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return normalize_organization_name(value)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=180)
    state: Optional[MexicanStateField] = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if value is None:
            raise ValueError("El nombre no puede ser nulo")
        return normalize_organization_name(value)

    @field_validator("state", mode="before")
    @classmethod
    def reject_null_state(cls, value: object) -> object:
        if value is None:
            raise ValueError("El estado no puede ser nulo")
        return value


class PaginatedOrganizations(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "name", "state"]
    direction: Literal["desc", "asc"]
    search: Optional[str] = None
    state: Optional[MexicanState] = None
    items: List[OrganizationDto] = Field(default_factory=list)


class TotalsOrganizations(BaseModel):
    total: int
    total_pages: int
    current_page: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
