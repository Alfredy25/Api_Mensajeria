from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.volante.repository import VolanteRepository
from app.api.v1.volante.schemas import VolanteDto, VolanteCreate, VolanteUpdate
from app.models import VolanteORM


class VolanteService:
    def __init__(self, db: Session, repo: VolanteRepository):
        self._db = db
        self._repo = repo

    def get_by_name(self, name: str) -> VolanteDto | None:
        return self._repo.get_by_name(name)

    def create_volante(self, volante: VolanteCreate) -> VolanteDto:
        volante_orm = self._repo.get_by_name(volante.name)
        if volante_orm:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Volante ya existe")
        volante_orm = VolanteORM(name=volante.name)
        try:
            volante_orm = self._repo.create(volante_orm)
            self._db.commit()
            self._db.refresh(volante_orm)
            return VolanteDto.model_validate(volante_orm, from_attributes=True)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise

    def get_by_id(self, volante_id: int) -> VolanteDto:
        volante_orm = self._repo.find_by_id(volante_id)
        if not volante_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Volante no existe"
            )
        return VolanteDto.model_validate(volante_orm, from_attributes=True)

    def update_volante(self, volante: VolanteUpdate):
        volante_orm = self._repo.find_by_id(volante.id)
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
        volante_orm = self._repo.get_by_name(volante.name)
        if volante_orm:
            return volante_orm

        volante_orm = VolanteORM(name=volante.name)

        volante_orm = self._repo.create(volante_orm)
        self._db.flush()
        return volante_orm






