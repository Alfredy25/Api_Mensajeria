from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.models import ContactORM


class ContactRepository(ABC):

    @abstractmethod
    def create(self, contact: ContactORM) -> ContactORM:
        ...

    @abstractmethod
    def update(self, contact_update: ContactORM, updates: dict) -> ContactORM:
        ...

    @abstractmethod
    def find_by_id(self, contact_id: int) -> ContactORM | None:
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

    def update(self, contact_update: ContactORM, updates: dict) -> ContactORM:
        for attr, value in updates.items():
            setattr(contact_update, attr, value)

        return contact_update