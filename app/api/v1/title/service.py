from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.v1.title.repository import TitleRepository
from app.api.v1.title.schemas import TitleDto, TitleUpdate, TitleCreate, PaginatedTitles
from app.models import TitleORM


class TitleService:
    def __init__(self, db: Session, repo: TitleRepository):
        self._db = db
        self._repo = repo

    def create_title(self, abbreviation: str, meaning: str) -> TitleDto:
        title_orm = self._repo.get_by_abbreviation(abbreviation)

        if title_orm:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El titulo ya existe",
            )
        try:
            title_orm = TitleORM(abbreviation=abbreviation, meaning=meaning)
            self._repo.create(title_orm)
            self._db.commit()
            self._db.refresh(title_orm)
            return TitleDto.model_validate(
                title_orm, from_attributes=True
            )
        except SQLAlchemyError as e:
            self._db.rollback()
            raise


    def get_titles(self,
                   search: str | None,
                   page: int,
                   limit: int,
                   order_by: Literal["id","abbrev", "meaning"],
                   direction: Literal["desc", "asc"],
                   ) -> PaginatedTitles:

        totals, titles = self._repo.get_titles(
            search=search.strip().upper() if search else None,
            page = page,
            limit = limit,
            order_by = order_by,
            direction = direction,
        )
        current_page = totals.current_page
        total = totals.total
        total_pages = totals.total_pages

        has_prev = current_page > 1 and total > 0
        has_next = current_page < total_pages if total_pages > 0 else False

        return PaginatedTitles(
            page= current_page,
            page_size=limit,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            order_by=order_by,
            direction=direction,
            search=search,
            items= [
                TitleDto.model_validate(title, from_attributes=True)
                for title in titles
            ]
        )

    def update_title(self, title_id, title_update: TitleUpdate) -> TitleDto:
        title = self._repo.find_by_id(title_id)
        if not title:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Titulo con id {title_id} no existe",
            )
        try:
            updates = title_update.model_dump(exclude_unset=True)
            title_orm = self._repo.update(title, updates)
            self._db.commit()
            self._db.refresh(title_orm)
            return TitleDto.model_validate(title_orm, from_attributes=True)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise

    def ensure_title(self, title: TitleCreate) -> TitleORM:
        title_orm = self._repo.get_by_abbreviation(title.abbreviation)
        if title_orm:
            return title_orm

        new_title_orm = TitleORM(abbreviation=title.abbreviation, meaning=title.meaning)
        title_orm = self._repo.create(new_title_orm)
        self._db.flush()
        return title_orm








