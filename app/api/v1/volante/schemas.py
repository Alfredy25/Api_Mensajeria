from typing import List

from pydantic import BaseModel, Field, ConfigDict


class VolanteDto(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class VolanteCreate(BaseModel):
    name: str = Field(..., min_length=19, max_length=35, examples=["VCS-26-131000-00167"])

class VolanteUpdate(BaseModel):
    name: str = Field(..., min_length=19, max_length=35, examples=["VCS-26-131000-00167"])

class PaginatedVolantes(BaseModel):
    search: str | None
    page: int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    items: List[VolanteDto] = Field(default_factory=list)

