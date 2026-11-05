from abc import ABC, abstractmethod
from math import ceil

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api.v1.contact.schemas import ContactUpdate, TotalsContacts
from app.models import ContactORM, ReceiverORM


class ContactRepository(ABC):

    @abstractmethod
    def create(self, contact: ContactORM) -> ContactORM:
        ...

    @abstractmethod
    def update(
        self,
        contact: ContactORM,
        contact_update: ContactUpdate,
    ) -> ContactORM:
        ...

    @abstractmethod
    def find_by_id(self, contact_id: int) -> ContactORM | None:
        ...

    @abstractmethod
    def receiver_exists(self, receiver_id: int) -> bool:
        ...

    @abstractmethod
    def list_by_receiver(self, receiver_id: int) -> list[ContactORM]:
        ...

    @abstractmethod
    def get_contacts(
        self,
        search: str | None,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsContacts, list[ContactORM]]:
        ...


class ContactRepositoryImpl(ContactRepository):

    def __init__(self, db: Session):
        self._db = db

    def create(self, contact: ContactORM) -> ContactORM:
        self._db.add(contact)
        self._db.flush()
        return contact

    def find_by_id(self, contact_id: int) -> ContactORM | None:
        return self._db.get(ContactORM, contact_id)

    def receiver_exists(self, receiver_id: int) -> bool:
        stmt = select(ReceiverORM.id).where(ReceiverORM.id == receiver_id)
        receiver_find = self._db.scalar(stmt)
        return receiver_find is not None

    def list_by_receiver(self, receiver_id: int) -> list[ContactORM]:
        stmt = select(ContactORM).where(
            ContactORM.id_destinatario == receiver_id
        )
        return list(self._db.scalars(stmt).all())

    def update(
        self,
        contact: ContactORM,
        contact_update: ContactUpdate,
    ) -> ContactORM:
        updates = contact_update.model_dump(exclude_unset=True)

        for field_name, value in updates.items():
            setattr(contact, field_name, value)

        return contact

    def get_contacts(
        self,
        search: str | None,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsContacts, list[ContactORM]]:
        stmt = self._apply_filters(select(ContactORM), search)
        total = self._count(search)
        totals = self._calculate_totals(total, page_size, page)
        offset = totals.offset

        stmt = self._apply_order(stmt, order_by, direction)
        contacts = list(
            self._db.scalars(
                stmt.offset(offset).limit(page_size)
            ).all()
        )
        return totals, contacts

    def _count(self, search: str | None) -> int:
        stmt = self._apply_filters(
            select(func.count()).select_from(ContactORM),
            search,
        )
        return self._db.scalar(stmt) or 0

    @staticmethod
    def _apply_filters(stmt: Select, search: str | None) -> Select:
        if search:
            term = f"%{search}%"
            stmt = stmt.where(ContactORM.phone.like(term))

        return stmt

    @staticmethod
    def _calculate_totals(
        total: int,
        page_size: int,
        page: int,
    ) -> TotalsContacts:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size

        return TotalsContacts(
            total=total,
            total_pages=total_pages,
            current_page=current_page,
            offset=offset,
        )

    @staticmethod
    def _apply_order(stmt: Select, order_by: str, direction: str) -> Select:
        if order_by == "phone":
            column = ContactORM.phone
        else:
            column = ContactORM.id

        if direction == "asc":
            return stmt.order_by(column.asc())

        return stmt.order_by(column.desc())
