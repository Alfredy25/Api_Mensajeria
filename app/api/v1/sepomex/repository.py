from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SepomexORM


class SepomexRepository(ABC):
    """Consultas del catálogo SEPOMEX."""

    @abstractmethod
    def find_by_postal_code(self, postal_code: str) -> list[SepomexORM]:
        """Devuelve los asentamientos de un código postal."""


class SepomexRepositoryImpl(SepomexRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_postal_code(self, postal_code: str) -> list[SepomexORM]:
        """Busca por igualdad exacta y ordena por nombre de asentamiento."""
        stmt = (
            select(SepomexORM)
            .where(SepomexORM.postal_code == postal_code)
            .order_by(SepomexORM.settlement.asc())
        )
        return list(self._db.scalars(stmt).all())
