from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.position import PositionORM



class JobRoleORM(Base): # Cargos
    __tablename__ = "job_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    abreviatura: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    significado: Mapped[str] = mapped_column(String(150), nullable=False)

    positions: Mapped[list["PositionORM"]] = relationship(
        "PositionORM",
        back_populates="job_role",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
