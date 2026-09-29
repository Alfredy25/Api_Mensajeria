from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from typing import List
from sqlalchemy import (Integer, String, Boolean, DateTime ,Table,
                        Column, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from .role import RoleORM
    from .register import RegisterORM

users_roles = Table(
    "users_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="unique_user_role"),
)


class UserORM(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True,nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    roles: Mapped[List[RoleORM]] = relationship("RoleORM",
                                                secondary=users_roles,
                                                lazy="selectin",
                                                back_populates="users",
                                                passive_deletes=True)
    registers: Mapped[list[RegisterORM]] = relationship("RegisterORM",
                                                        back_populates="created_by_user",
                                                        lazy="selectin")

