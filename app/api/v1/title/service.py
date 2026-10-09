from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.v1.title.repository import TitleRepository
from app.api.v1.title.schemas import TitleDto, TitleUpdate
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
            return TitleDto.model_validate(
                title_orm, from_attributes=True
            )
        except SQLAlchemyError as e:
            self._db.rollback()
            raise


    def get_titles(self) -> List[TitleDto]:
        titles = self._repo.get_titles()
        return [
            TitleDto.model_validate(title, from_attributes=True)
            for title in titles
        ]

    def update_title(self, title_id, title_update: TitleUpdate) -> TitleDto:
        title = self._repo.find_by_id(title_id)
        if not title:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Titulo con id {title_id} no existe",
            )
        try:
            updates = title_update.model_dump(exclude_unset=True)
            title_dto = self._repo.update(title, updates)
            self._db.commit()
            self._db.refresh(title_dto)
            return TitleDto.model_validate(title_dto, from_attributes=True)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise

    def ensure_title(self, abbreviation: str, meaning: str) -> TitleORM:
        title_orm = self._repo.get_by_abbreviation(abbreviation)
        if title_orm:
            return title_orm

        new_title_orm = TitleORM(abbreviation=abbreviation, meaning=meaning)
        title_orm = self._repo.create(new_title_orm)
        self._db.flush()
        return title_orm








