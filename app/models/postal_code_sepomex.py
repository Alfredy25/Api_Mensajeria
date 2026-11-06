from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class SepomexORM(Base):
    __tablename__ = "cat_sepomex"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    postal_code: Mapped[str] = mapped_column(String(5), index=True)
    settlement: Mapped[str] = mapped_column(String(100), nullable=False)
    settlement_type: Mapped[str] = mapped_column(String(60), nullable=False)
    municipality: Mapped[str] = mapped_column(String(60), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    state_code: Mapped[str] = mapped_column(String(2), nullable=False)
    zone: Mapped[str] = mapped_column(String(30), nullable=False)


