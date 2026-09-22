from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base
if TYPE_CHECKING:
    from app.models.job_role import JobRoleORM
    from app.models.organization import OrganizationORM
    from app.models.receiver import ReceiverORM


class PositionORM(Base): # Puestos (Tabla Intermedia con Identidad)
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("job_id", "organization_id", name="uq_job_organization"),
                      )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"),nullable=False)

    job_role: Mapped["JobRoleORM"] = relationship("JobRoleORM", back_populates="positions")
    organization: Mapped["OrganizationORM"] = relationship("OrganizationORM", back_populates="positions")
    receivers: Mapped[list["ReceiverORM"]] = relationship("ReceiverORM", back_populates="position")