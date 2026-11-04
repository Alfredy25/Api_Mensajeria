from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import AfterValidator

from app.api.v1.job_role.schemas import JobCreate, JobDto, JobUpdate, PaginatedJobs
from app.api.v1.job_role.service import JobService
from app.api.v1.receiver.schemas import normalize_search
from app.core.dependencies import get_job_service

router = APIRouter(prefix="/job-roles", tags=["job-roles"])


@router.get("/", response_model=PaginatedJobs)
def list_jobs(
    search: Optional[
        Annotated[
            str,
            Query(
                default=None,
                min_length=3,
                max_length=60,
                pattern=r"^[a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ.\s]+$",
                description="Texto para buscar por abreviatura o significado",
                examples=["DIR.", "director", "PDTE."],
            ),
            AfterValidator(normalize_search),
        ]
    ] = None,
    page: int = Query(
        default=1,
        ge=1,
        description="Número de página (>=1)",
    ),
    page_size: int = Query(
        default=50,
        ge=5,
        le=80,
        description="Cantidad de cargos (5-80)",
    ),
    order_by: Literal["id", "abbreviation", "meaning"] = Query(
        default="id",
        description="Campo de orden",
    ),
    direction: Literal["desc", "asc"] = Query(
        default="asc",
        description="Dirección del orden",
    ),
    service: JobService = Depends(get_job_service),
) -> PaginatedJobs:
    return service.get_jobs(
        search=search,
        page=page,
        limit=page_size,
        order_by=order_by,
        direction=direction,
    )

@router.get("/{job_id}", response_model=JobDto)
def get_job(job_id: int = Path(...,description="Identificador del cargo"),
            service: JobService = Depends(get_job_service),):
    return service.get_job(job_id = job_id)


@router.post("/", response_model=JobDto, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    service: JobService = Depends(get_job_service),
) -> JobDto:
    return service.create_job(job)


@router.patch("/{job_id}", response_model=JobDto)
def update_job(
    job_id: int = Path(
        ...,
        ge=1,
        description="Identificador del cargo a actualizar",
        examples=[1],
    ),
    job: JobUpdate = Body(..., description="Campos del cargo a actualizar"),
    service: JobService = Depends(get_job_service),
) -> JobDto:
    return service.update_job(job_id=job_id, job=job)
