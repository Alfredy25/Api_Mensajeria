from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict


class TitleDto(BaseModel):
    id: int
    abbreviation: str
    meaning: str

    model_config = ConfigDict(from_attributes=True)

class TitleCreate(BaseModel):
    abbreviation: str = Field(..., min_length=3, max_length=60,  examples=["DR."],description="Title abbreviation")
    meaning: str = Field(..., min_length=3, max_length=150, examples=["Doctor"],description="Meaning from title abbreviation")  # Significado

class TitleUpdate(BaseModel):
    abbreviation: Optional[str] = Field(default=None, max_length=60)
    meaning: Optional[str] = Field(default=None, max_length=150)

class PaginatedTitles(BaseModel):
    page:int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id","abbrev", "meaning"]
    direction: Literal["desc", "asc"]
    search: Optional[str] = None
    items: List[TitleDto] = Field(default_factory=list)

class TotalsTitles(BaseModel):
    total: int
    total_pages: int
    current_page: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
