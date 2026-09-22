from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.receiver import ReceiverORM

class ContactORM(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    ext: Mapped[str | None] = mapped_column(String(5), nullable=True)
    email: Mapped[str | None] = mapped_column(String(60), nullable=True)

    id_destinatario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("receivers.id", ondelete="CASCADE"),
        nullable=False
    )

    receiver: Mapped["ReceiverORM"] = relationship(
        "ReceiverORM",
        back_populates="contacts"
    )