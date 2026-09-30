from datetime import datetime, timezone
from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Enum as SQLEnum, DateTime
from typing import List
from app.core.db import Base

if TYPE_CHECKING:
    from .user import UserORM

class NameRole(str, Enum):
    ADMIN = "Admin"
    OPERATOR = "Operator"
    CLIENT = "Client"


class RoleORM(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[NameRole] = mapped_column(
        SQLEnum(NameRole, name="role_name_enum"),
        nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    users: Mapped[List[UserORM]] = relationship("UserORM",
                                                secondary="users_roles",
                                                back_populates="roles",
                                                lazy="selectin")