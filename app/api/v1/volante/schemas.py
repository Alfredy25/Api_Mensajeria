from pydantic import BaseModel, Field, ConfigDict


class VolanteDto(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class VolanteCreate(BaseModel):
    name: str = Field(..., max_length=50)

class VolanteUpdate(VolanteCreate):
    id: int = Field(..., description='id del volante a actualizar')
