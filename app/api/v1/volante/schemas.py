from pydantic import BaseModel, Field

class VolanteDto(BaseModel):
    id: int
    name: str

class VolanteCreate(BaseModel):
    name: str = Field(..., max_length=50)

class VolanteUpdate(VolanteCreate):
    id: int = Field(..., description='id del volante a actualizar')
