from abc import ABC, abstractmethod

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import VolanteORM, TitleORM


class VolanteRepository(ABC):

    @abstractmethod
    def create(self, title: VolanteORM) -> VolanteORM:
        ...

    @abstractmethod
    def get_volantes(self) -> list[VolanteORM]:
        ...

    @abstractmethod
    def find_by_id(self, title_id: int) -> VolanteORM | None:
        ...

    @abstractmethod
    def update(self, title: VolanteORM, updates: dict) -> VolanteORM:
        ...

    @abstractmethod
    def get_by_name(self, abbreviation: str) -> VolanteORM | None:
        ...

class VolanteRepositoryImpl(VolanteRepository):

    def __init__(self, db: Session):
        self._db = db

    def create(self, volante: VolanteORM) -> VolanteORM:
        self._db.add(volante)
        self._db.flush()
        return volante

    def find_by_id(self, volante_id: int) -> VolanteORM | None:
        return self._db.get(VolanteORM, volante_id)

    def get_by_name(self, name: str) -> VolanteORM | None:
        volante_orm = self._db.execute(
            select(VolanteORM).where(
                VolanteORM.name == func.upper(name)
            )
        ).scalar_one_or_none()

        return volante_orm

    def get_volantes(self) -> list[VolanteORM]:
        volantes_orm = self._db.scalars(  # Revisar después con created_at nos traeremos todos los creados en ese dia actual
            select(VolanteORM).order_by(
                VolanteORM.name.asc()
            )
        ).all()
        return list(volantes_orm)

    def update(self, title: VolanteORM, updates: dict) -> VolanteORM:
        for attr, value in updates.items():
            setattr(title, attr, value)
        return title