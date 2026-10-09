from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class JobDto(BaseModel):
    id: int
    abbreviation: str
    meaning: str

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    abbreviation: str = Field(..., min_length=3, max_length=60)
    meaning: str = Field(..., min_length=3, max_length=150)

class JobUpdate(BaseModel):
    abbreviation: Optional[str] = None
    meaning: Optional[str] = None