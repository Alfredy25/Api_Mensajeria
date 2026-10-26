from typing import List, Literal, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from app.api.v1.volante.schemas import VolanteDto, PaginatedVolantes, VolanteCreate, VolanteUpdate
from app.api.v1.volante.service import VolanteService
from app.core.dependencies import get_volante_service

router = APIRouter(prefix="/volante", tags=["volantes"])

@router.get("/", response_model=PaginatedVolantes)
def get_volantes(
        search: Optional[str] = Query(
            default=None,
            max_length=50,
            min_length=3,
            pattern=r"^[A-Za-z0-9\-]+$",
            description="Texto para buscar con patron",
            examples=["VSC-26", "131000", "-00210", "131000-", "167"],
        ),
        page: int = Query(default=1, ge=1, le=100, description="pagina solicitada"),
        page_size: int = Query(default=50, ge=5, le=100, description="cantidad de volantes"),
        order_by: Literal["id", "name"] = Query(default="id", description="orden de los volantes"),
        direction: Literal["desc", "asc"] = Query(default="asc",description="dirección de orden"),
        service: VolanteService = Depends(get_volante_service)) -> PaginatedVolantes:
    return service.find_all(
        search, page, page_size, order_by, direction
    )

@router.post("/", response_model=VolanteDto, status_code=status.HTTP_201_CREATED)
def create_volante(
        volante: VolanteCreate,
        service: VolanteService = Depends(get_volante_service)):
    return service.create_volante(volante)

@router.patch("/{volante_id}", response_model=VolanteDto)
def update_volante(volante_id: int = Path(...,
                                          ge=1,
                                          title="Id del volante a actualizar",
                                          description="Identificador entero del volante debe ser mayor o igual a 1",
                                          examples=[1,3,20]),
                   data: VolanteUpdate = Body(..., description="json del volante a actualizar"),
                   service: VolanteService = Depends(get_volante_service),):
    return service.update_volante(volante_id, data)
