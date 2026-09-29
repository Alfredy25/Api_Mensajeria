from pydantic import BaseModel, Field


class ReceiverDto(BaseModel):
    id: int = Field(..., examples=[])


class ReceiverCreate(BaseModel):
    pass


class ReceiverUpdate(BaseModel):
    pass