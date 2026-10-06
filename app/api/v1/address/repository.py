from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.api.v1.address.schemas import AddressUpdate, AddressCreate
from app.models import AddressORM


class AddressRepository(ABC):

    @abstractmethod
    def create(self, new_address: AddressORM) -> AddressORM:
        ...

    @abstractmethod
    def update(self, address_orm: AddressORM, address_update: AddressUpdate) -> AddressORM:
        pass

    @abstractmethod
    def find_by_id(self, address_id: int) -> AddressORM:
        pass


class AddressRepositoryImpl(AddressRepository):

    def __init__(self, db: Session):
        self._db = db

    def create(self, new_address: AddressORM) -> AddressORM:
        self._db.add(new_address)
        self._db.flush()
        return new_address

    def find_by_id(self, address_id: int) -> AddressORM | None:
        return self._db.get(AddressORM, address_id)

    def update(self, address_orm: AddressORM, address_update: AddressUpdate) -> AddressORM:
        address_update = address_update.model_dump(exclude_unset=True)

        for attr, value in address_update.items():
            setattr(address_orm, attr, value)

        return address_orm


