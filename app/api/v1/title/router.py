from fastapi import APIRouter, Depends, status
from typing import List

from app.api.v1.title.schemas import TitleDto, TitleCreate, TitleUpdate
from app.core.dependencies import get_title_service

router = APIRouter(prefix="/titles", tags=["titles"])

@router.get("/", response_model=List[TitleDto])
def get_titles(service_title = Depends(get_title_service)):
    return service_title.get_titles()

@router.post("/", response_model=TitleDto, status_code=status.HTTP_201_CREATED)
def create_title(title: TitleCreate, service_title = Depends(get_title_service)):
    return service_title.create_title(
        abbreviation = title.abbreviation,
        meaning = title.meaning,
    )

@router.patch("/{title_id}", response_model=TitleDto)
def update_title(title_id: int, title: TitleUpdate,
                 service_title = Depends(get_title_service)):
    return service_title.update_title(title_id=title_id, title_update=title)
