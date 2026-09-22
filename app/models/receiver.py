from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import (Integer, String, Enum as SQLEnum, DateTime, func, ForeignKey,
                        UniqueConstraint, Table, Column)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.position import PositionORM
    from app.models.titulo import TitleORM
    from app.models.address import AddressORM
    from app.models.contac import ContactORM
    from app.models.volante import VolanteORM


class EntidadesEnum(str, PyEnum):
    PERSONA = "PERSONA"
    PRIVADA = "PRIVADA"
    GOBIERNO = "GOBIERNO"


receiver_volante = Table(
    "receiver_volante",
    Base.metadata,
    Column("receiver_id", Integer, ForeignKey("receivers.id", ondelete="CASCADE")),
    Column("volante_id", Integer, ForeignKey("volantes.id", ondelete="CASCADE")),
    UniqueConstraint("receiver_id", "volante_id", name="unique_receiver_id"),
)

class ReceiverORM(Base):
    __tablename__ = "receivers"
    __table_args__ = (
        UniqueConstraint("full_name", "title_id", "position_id", name="uq_receiver_name_position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    tipo_entidad: Mapped[str] = mapped_column(SQLEnum(EntidadesEnum, name="entidades_enum"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(70), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(timezone.utc), nullable=False)

    title_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("titles.id", ondelete="SET NULL"), nullable=True)
    position_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)

    titulo: Mapped["TitleORM"] = relationship("TitleORM", lazy="joined")
    position: Mapped["PositionORM"] = relationship("PositionORM", back_populates="receivers", lazy="joined")
    addresses: Mapped[list["AddressORM"]] = relationship(
        "AddressORM",
        lazy="selectin",
        cascade="all, delete, delete-orphan"
    )
    contacts: Mapped[list["ContactORM"]] = relationship(
        "ContactORM",
        lazy="selectin",
        cascade="all, delete, delete-orphan"
    )

    volantes: Mapped[list["VolanteORM"]] = relationship(
        secondary="receiver_volante",
        back_populates="receivers",
        lazy="selectin",
        passive_deletes=True,
    )

