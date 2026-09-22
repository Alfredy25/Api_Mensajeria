from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models import ReceiverORM


class VolanteORM(Base):
    __tablename__ = 'volantes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    receivers: Mapped[list["ReceiverORM"]] = relationship(
        secondary="receiver_volante",
        back_populates="volantes",
        lazy="selectin"
    )