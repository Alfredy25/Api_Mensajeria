from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional, Annotated, Literal

from pydantic import AfterValidator

from app.api.v1.receiver.schemas import normalize_search
from app.api.v1.title.schemas import TitleDto, TitleCreate, TitleUpdate, PaginatedTitles
from app.core.dependencies import get_title_service

router = APIRouter(prefix="/titles", tags=["titles"])

@router.get("/", response_model=PaginatedTitles)
def list_titles(
        search: Optional[
            Annotated[
                str,
                Query(
                    default=None,
                    maxlength=60,
                    min_length=2,
                    pattern="^[a-zA-Z0-9áéíóúÁÉÍÓÚ.\s]+$",
                    description="Search titles by abbreviation and meaning",
                    examples=["ABG.","Abogado","Doctor","GOB."]
                ),
                AfterValidator(normalize_search)
            ]
        ] = None,
        page: int = Query(
            default=1,
            ge=1,
            description="Page number >=1",
        ),
        page_size: int = Query(
            default=50, ge=5, le=80,
            description="Number of results to return",
        ),
        order_by: Literal["id","abbrev", "meaning"] = Query(
            default="id",
            description="Order column"
        ),
        direction: Literal["desc", "asc"] = Query(default="asc", description="Direction of order"),
        service_title = Depends(get_title_service)):
    return service_title.get_titles(
        search=search, page = page, limit=page_size, order_by=order_by,
        direction=direction
    )

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
