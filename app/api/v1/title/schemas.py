from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TitleDto(BaseModel):
    id: int
    abbreviation: str
    meaning: str

    model_config = ConfigDict(from_attributes=True)

class TitleCreate(BaseModel):
    abbreviation: str = Field(..., min_length=3, max_length=60)
    meaning: str = Field(..., min_length=3, max_length=150)  # Significado

class TitleUpdate(BaseModel):
    abbreviation: Optional[str] = Field(default=None, max_length=60)
    meaning: Optional[str] = Field(default=None, max_length=150)