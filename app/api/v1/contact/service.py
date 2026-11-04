from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.contact.repository import ContactRepository
from app.api.v1.contact.schemas import (
    ContactCreate,
    ContactDto,
    ContactUpdate,
    PaginatedContacts,
)
from app.models import ContactORM


class ContactService:

    def __init__(self, db: Session, repo: ContactRepository):
        self._db = db
        self._repo = repo

    def create_contact(
        self,
        receiver_id: int,
        contact: ContactCreate,
    ) -> ContactDto:
        self._require_receiver(receiver_id)
        self._reject_duplicate(
            receiver_id,
            self._duplicate_key(contact.phone, contact.ext),
        )

        created = self._repo.create(
            self._to_contact_orm(contact, receiver_id)
        )
        return self._commit(created)

    def _require_receiver(self, receiver_id: int) -> None:
        if self._repo.receiver_exists(receiver_id):
            return

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destinatario con id {receiver_id} no existe",
        )

    def _reject_duplicate(
        self,
        receiver_id: int,
        incoming_key: tuple[str, str | None],
    ) -> None:
        duplicates = self._find_duplicates(receiver_id, incoming_key)
        if duplicates:
            self._raise_duplicate(duplicates[0].id)

    def _find_duplicates(
        self,
        receiver_id: int,
        incoming_key: tuple[str, str | None],
    ) -> list[ContactORM]:
        return [
            contact
            for contact in self._repo.list_by_receiver(receiver_id)
            if self._duplicate_key(contact.phone, contact.ext) == incoming_key
        ]

    @staticmethod
    def _duplicate_key(
        phone: str | None, ext: str | None,
    ) -> tuple[str, str | None]:
        normalized_phone = phone.strip() if phone else ""
        normalized_ext = ext.strip() if ext else None
        return normalized_phone, normalized_ext or None

    @staticmethod
    def _raise_duplicate(contact_id: int) -> None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El destinatario ya tiene un contacto con ese teléfono y extensión"
        )

    @staticmethod
    def _to_contact_orm(
            contact: ContactCreate, receiver_id: int
    ) -> ContactORM:
        return ContactORM(
            phone=contact.phone,
            ext=contact.ext if contact.ext else None,
            id_destinatario=receiver_id,
        )

    def _commit(self, contact: ContactORM) -> ContactDto:
        try:
            self._db.commit()
            self._db.refresh(contact)
            return ContactDto.model_validate(contact)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def list_contacts(
        self,
        search: str | None,
        page: int,
        page_size: int,
        order_by: Literal["id", "phone"],
        direction: Literal["asc", "desc"],
    ) -> PaginatedContacts:
        totals, contacts = self._repo.get_contacts(
            search=search,
            page=page,
            page_size=page_size,
            order_by=order_by,
            direction=direction,
        )

        current_page = totals.current_page
        total = totals.total
        total_pages = totals.total_pages
        has_prev = current_page > 1 and total > 0
        has_next = total_pages > 0 and current_page < total_pages

        return PaginatedContacts(
            page=current_page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            order_by=order_by,
            direction=direction,
            search=search,
            items=[
                ContactDto.model_validate(contact)
                for contact in contacts
            ],
        )

    def update_contact(
        self, contact_id: int, contact: ContactUpdate
    ) -> ContactDto:

        current = self._find_contact(contact_id)
        incoming_key = self._duplicate_key_after_update(current, contact)
        self._reject_duplicate_of_another(current, incoming_key)

        updated = self._repo.update(current, contact)
        return self._commit(updated)

    def _find_contact(self, contact_id: int) -> ContactORM:
        contact = self._repo.find_by_id(contact_id)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contacto con id {contact_id} no existe",
            )

        return contact

    @staticmethod
    def _duplicate_key_after_update(
        current: ContactORM, contact_update: ContactUpdate
    ) -> tuple[str, str | None]:
        changes: dict[str, str | None] = contact_update.model_dump(
            exclude_unset=True,
        )
        phone = ContactService._incoming_or_current(current, changes, "phone")
        ext = ContactService._incoming_or_current(current, changes, "ext")
        return ContactService._duplicate_key(phone, ext)

    @staticmethod
    def _incoming_or_current(
        current: ContactORM,
        changes: dict[str, str | None],
        field_name: str,
    ) -> str | None:
        if field_name not in changes:
            return getattr(current, field_name)

        return changes[field_name]

    def _reject_duplicate_of_another(
        self,
        current: ContactORM,
        incoming_key: tuple[str, str | None],
    ) -> None:
        duplicates = self._find_duplicates(
            current.id_destinatario,
            incoming_key,
        )
        other_duplicates = [
            contact for contact in duplicates if contact.id != current.id
        ]
        if other_duplicates:
            self._raise_duplicate(other_duplicates[0].id)

    def create_contact_with_receiver(self, contact: ContactCreate) -> ContactORM:
        contact_orm = ContactORM(
            phone=contact.phone,
            ext=contact.ext if contact.ext else None
        )
        return contact_orm
