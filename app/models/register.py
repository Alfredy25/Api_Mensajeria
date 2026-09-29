from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from app.core.db import Base
from datetime import datetime, timezone
from .user import UserORM

class Sede(str, Enum):
    AJUSCO = 'AJUSCO'
    COYOACAN = 'COYOACAN'


class RegisterORM(Base):
    __tablename__ = 'registers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sede: Mapped[str] =mapped_column(SQLEnum(Sede, name="sede_enum"), default=Sede.AJUSCO, nullable=False, index=True)
    image_name: Mapped[str] = mapped_column(String(50), nullable=False)

    raw_receiver: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    position_dependency: Mapped[str| None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255))
    colony: Mapped[str | None] = mapped_column(String(255))
    municipality: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(6))

    number_volante: Mapped[str | None] = mapped_column(String(50))
    extras: Mapped[str | None] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(150))
    instructions: Mapped[str | None] = mapped_column(String(200))

    ai_notes: Mapped[str | None] = mapped_column(String(200))
    crop_x: Mapped[int] = mapped_column(Integer, nullable=False)
    crop_y: Mapped[int] = mapped_column(Integer, nullable=False)
    crop_w: Mapped[int] = mapped_column(Integer, nullable=False)
    crop_h: Mapped[int] = mapped_column(Integer, nullable=False)
    rotation_deg: Mapped[int | None] = mapped_column(Integer)

    aspect_mode: Mapped[str | None] = mapped_column(String(55), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(timezone.utc), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(timezone.utc), onupdate=func.now(timezone.utc), nullable=False)

    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    created_by_user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="registers",
        lazy="joined")







