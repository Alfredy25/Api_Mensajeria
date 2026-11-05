from abc import ABC, abstractmethod
from math import ceil

from sqlalchemy import select, func, or_, Select
from sqlalchemy.orm import Session

from app.api.v1.title.schemas import TotalsTitles
from app.models import TitleORM


class TitleRepository(ABC):

    @abstractmethod
    def create(self, title: TitleORM) -> TitleORM:
        ...

    @abstractmethod
    def get_titles(self,
                   search: str | None,
                   page: int,
                   limit: int,
                   order_by: str,
                   direction: str
                   ) -> tuple[TotalsTitles, list[TitleORM]]:
        ...

    @abstractmethod
    def find_by_id(self, title_id: int) -> TitleORM | None:
        ...

    @abstractmethod
    def update(self, title: TitleORM, updates: dict) -> TitleORM:
        ...

    @abstractmethod
    def get_by_abbreviation(self, abbreviation: str) -> TitleORM | None:
        ...

class TitleRepositoryImpl(TitleRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_id(self, title_id: int) -> TitleORM | None:
        return self._db.get(
            TitleORM, title_id
        )

    def get_titles(self,
                   search: str | None,
                   page: int,
                   limit: int,
                   order_by: str,
                   direction: str
                   ) -> tuple[TotalsTitles, list[TitleORM]]:

        stmt = select(TitleORM)
        if search:
            stmt = stmt.where(
                or_(
                    TitleORM.abbreviation.like(f"%{search}%"),
                    func.upper(TitleORM.meaning).like(f"%{search}%"),
                )
            )

        total = self.get_total(search)
        totals = self._calculate_totals(
            total, limit, page
        )
        offset = totals.offset

        stmt = self.apply_order(stmt, order_by, direction)

        titles = list(
            self._db.scalars(
                stmt.offset(offset).limit(limit)
            ).all()
        )

        return totals, titles

    def get_total(self, search: str | None) -> int:
        total_count = select(func.count()).select_from(TitleORM)
        if search:
            total_count = total_count.where(
                or_(
                    TitleORM.abbreviation.like(f"%{search}%"),
                    func.upper(TitleORM.meaning).like(f"%{search}%"),
                )
            )
        return self._db.scalar(total_count) or 0

    @staticmethod
    def _calculate_totals(total: int, page_size: int, page: int) -> TotalsTitles:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size

        return TotalsTitles(
            total = total,
            total_pages = total_pages,
            current_page = current_page,
            offset = offset,
        )

    @staticmethod
    def apply_order(stmt: 'Select', order_by: str, direction: str) -> 'Select':
        if order_by == 'meaning':
            order_col = TitleORM.meaning
        elif order_by == 'abbrev':
            order_col = TitleORM.abbreviation
        else:
            order_col = TitleORM.id

        return stmt.order_by(
            order_col.asc() if direction == 'asc' else order_col.desc()
        )

    def update(self, title: TitleORM, updates: dict) -> TitleORM:
        for attr, value in updates.items():
            setattr(title, attr, value)
        return title

    def get_by_abbreviation(self, abbreviation: str) -> TitleORM | None:
        title_orm = self._db.execute(
            select(TitleORM).where(
                TitleORM.abbreviation == func.upper(abbreviation)
            )
        ).scalar_one_or_none()
        return title_orm

    def create(self, title: TitleORM) -> TitleORM:
        self._db.add(title)
        self._db.flush()
        return title