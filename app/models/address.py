from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
if TYPE_CHECKING:
    from app.models import ReceiverORM



class AddressORM(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(100), nullable=False)
    num_street: Mapped[str] = mapped_column(String(50), nullable=False)
    colony: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    address_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("receivers.id", ondelete="CASCADE"),
        nullable=False
    )

    receiver: Mapped["ReceiverORM"] = relationship(
        "ReceiverORM",
        back_populates="addresses",
    )

