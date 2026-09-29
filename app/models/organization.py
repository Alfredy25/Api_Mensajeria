from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.position import PositionORM


class OrganizationORM(Base): # dependencias
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("name", "state", name="uq_state_name"),
                      )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str | None] = mapped_column(String(60), nullable=False)

    positions: Mapped[list["PositionORM"]] = relationship(
        "PositionORM",
        lazy="selectin",
        back_populates="organization",
        cascade="all, delete-orphan"
    )