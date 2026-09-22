from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped

from app.core.db import Base

class TitleORM(Base):
    __tablename__ = "titles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    abreviatura: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    significado: Mapped[str] = mapped_column(String(150), nullable=False)