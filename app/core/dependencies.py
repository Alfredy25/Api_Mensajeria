from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.title.repository import TitleRepositoryImpl, TitleRepository
from app.api.v1.title.service import TitleService
from app.core.db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencias Title
def get_title_repository(db: Session = Depends(get_db)):
    return TitleRepositoryImpl(db=db)

def get_title_service(db: Session = Depends(get_db),
                      repository: TitleRepository = Depends(get_title_repository)):
    return TitleService(db=db, repo= repository)