from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.contact.repository import ContactRepository
from app.api.v1.contact.schemas import ContactCreate, ContactDto, ContactUpdate
from app.models import ContactORM


class ContactService:
    def __init__(self, db: Session, repo: ContactRepository):
        self._db = db
        self._repo = repo

    def create_contact(self, contact: ContactCreate) -> ContactDto:
        contact_orm = ContactORM(
            phone=contact.phone,
            ext=contact.ext if contact.ext else None
        )
        try:
            contact_orm_new = self._repo.create(contact_orm)
            self._db.commit()
            return ContactDto.model_validate(contact_orm_new, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def update_contact(self, contact_id, contact: ContactUpdate) -> ContactDto:
        contact_orm = self._repo.find_by_id(contact_id=contact_id)
        updates = contact.model_dump(exclude_unset=True)
        try:
            contact_orm_update = self._repo.update(contact_orm, updates)
            self._db.commit()
            return ContactDto.model_validate(contact_orm_update, from_attributes=True)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    def create_contact_with_receiver(self, contact: ContactCreate) -> ContactORM:
        contact_orm = ContactORM(
            phone=contact.phone,
            ext=contact.ext if contact.ext else None
        )
        return self._repo.create(contact_orm)

