from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.volante.repository import VolanteRepository
from app.api.v1.volante.schemas import VolanteDto, VolanteCreate, PaginatedVolantes, VolanteUpdate
from app.models import VolanteORM


class VolanteService:
    def __init__(self, db: Session, repo: VolanteRepository):
        self._db = db
        self._repo = repo

    def find_all(self,
                 search: str | None,
                 page: int,
                 page_size: int,
                 order_by: str,
                 direction: str) -> PaginatedVolantes:
        search_find = search.strip().upper() if search else None

        totals, volantes_orm = self._repo.list_all(
            search_find, page, page_size, order_by, direction
        )

        total = totals.get("total")
        total_pages = totals.get("total_pages")
        current_page = totals.get("current_page")

        has_prev = current_page > 1 and total > 0
        has_next = current_page < total_pages if total_pages > 0 else False

        items = [
            VolanteDto.model_validate(volante_orm, from_attributes=True)
            for volante_orm in volantes_orm
        ]
        return PaginatedVolantes(
            search=search_find,
            page=current_page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_prev=has_prev,
            has_next=has_next,
            items = items
        )

    def create_volante(self, volante: VolanteCreate) -> VolanteDto:
        volante_orm = self._repo.get_by_name(volante.name.upper())
        if volante_orm:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Volante ya existe")

        volante.name = volante.name.strip().upper()
        try:
            volante_orm = self._repo.create(volante.name.upper())
            self._db.commit()
            self._db.refresh(volante_orm)
            return VolanteDto.model_validate(volante_orm, from_attributes=True)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise

    def get_by_name(self, name: str) -> VolanteDto:
        volante_orm = self._repo.get_by_name(name)
        if not volante_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volante no existe"
            )
        return VolanteDto.model_validate(volante_orm, from_attributes=True)

    def get_by_id(self, volante_id: int) -> VolanteDto:
        volante_orm = self._repo.find_by_id(volante_id)
        if not volante_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volante no existe"
            )
        return VolanteDto.model_validate(volante_orm, from_attributes=True)

    def update_volante(self, volante_id: int, volante: VolanteUpdate):
        volante_orm = self._repo.find_by_id(volante_id)
        if not volante_orm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Volante no existe")
        updates = volante.model_dump()
        try:
            volante_orm = self._repo.update(volante_orm, updates)
            self._db.commit()
            self._db.refresh(volante_orm)
            return VolanteDto.model_validate(volante_orm, from_attributes=True)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise

    def ensure_volante(self, volante: VolanteCreate) -> VolanteORM:
        volante_orm = self._repo.get_by_name(volante.name.upper())
        if volante_orm:
            return volante_orm

        volante_orm_new = self._repo.create(volante.name.upper())
        self._db.flush()
        return volante_orm_new






