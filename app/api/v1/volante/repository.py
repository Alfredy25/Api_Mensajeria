from abc import ABC, abstractmethod
from math import ceil
from typing import Any

from sqlalchemy import select, func, Select
from sqlalchemy.orm import Session

from app.models import VolanteORM


class VolanteRepository(ABC):

    @abstractmethod
    def list_all(self,
                 search: str | None,
                 page: int,
                 page_size: int,
                 order_by: str,
                 direction) -> tuple[dict[str, Any], list[VolanteORM]]:
        ...

    @abstractmethod
    def create(self, name: str) -> VolanteORM:
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

    def list_all(self,
                 search: str | None,
                 page: int,
                 page_size: int,
                 order_by: str,
                 direction) -> tuple[dict[str, Any], list[VolanteORM]]:

        stmt = (select(VolanteORM))
        if search:
            stmt = stmt.where(VolanteORM.name.like(f"%{search}%"))

        total = self._get_total(search)
        total_pages, current_page, offset = self._calculate_totals(
            total, page_size, page
        )

        stmt = self._apply_order(order_by, direction, stmt)
        volantes =  list(
            self._db.scalars(
                stmt.offset(offset).limit(page_size)
            ).all()
        )

        totals = {
            "total": int(total),
            "total_pages": int(total_pages),
            "current_page": int(current_page)
        }

        return totals, volantes

    def _get_total(self, search: str | None) -> int:
        total_count = select(func.count()).select_from(VolanteORM)
        if search:
            total_count = total_count.where(
                VolanteORM.name.like(f"%{search}%")
            )

        return self._db.scalar(total_count) or 0

    @staticmethod
    def _calculate_totals(total: int, page_size: int, page: int) -> tuple[int, int, int]:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size
        return total_pages, current_page, offset

    @staticmethod
    def _apply_order(order_by: str, direction: str, stmt: 'Select') -> 'Select':
        if order_by == "name":
            order_col = VolanteORM.name
        else:
            order_col = VolanteORM.id

        return stmt.order_by(
            order_col.asc() if direction == "asc" else order_col.desc()
        )

    def create(self, name: str) -> VolanteORM:
        volante_new = VolanteORM(name=name)
        self._db.add(volante_new)
        self._db.flush()
        return volante_new

    def find_by_id(self, volante_id: int) -> VolanteORM | None:
        return self._db.get(VolanteORM, volante_id)

    def get_by_name(self, name: str) -> VolanteORM | None:
        volante_orm = self._db.execute(
            select(VolanteORM).where(
                VolanteORM.name == func.upper(name)
            )
        ).scalar_one_or_none()
        return volante_orm

    def update(self, volante: VolanteORM, updates: dict) -> VolanteORM:
        for attr, value in updates.items():
            setattr(volante, attr, value)
        return volante