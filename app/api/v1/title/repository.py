from abc import ABC, abstractmethod

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import TitleORM


class TitleRepository(ABC):

    @abstractmethod
    def create(self, title: TitleORM) -> TitleORM:
        ...

    @abstractmethod
    def get_titles(self) -> list[TitleORM]:
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

    def get_titles(self) -> list[TitleORM]:
        return list(
            self._db.scalars(
                select(TitleORM)
            )
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