from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.address.repository import AddressRepository
from app.api.v1.address.schemas import AddressCreate, AddressDto, AddressUpdate
from app.models import AddressORM


class AddressService:
    def __init__(self, repo: AddressRepository, db: Session):
        self._repo = repo
        self._db = db

    def create_address(self, address_create: AddressCreate) -> AddressDto:

        new_address = AddressORM(
                    street = address_create.street,
                    num_street = address_create.num_street,
                    state = address_create.state,
                    colony = address_create.colony,
                    postal_code = address_create.postal_code,
                    city = address_create.city,
                    country = address_create.country,
                    address_reference = address_create.address_reference
                )
        address_orm = self._repo.create(new_address)
        self._db.commit()
        self._db.refresh(address_orm)
        return AddressDto.model_validate(address_orm)

    def update_address(self, address_update: AddressUpdate, address_id) -> AddressDto:
        address_orm = self._repo.find_by_id(address_id)
        if not address_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No address found with id {address_id}"
            )
        address_orm_update = self._repo.update(address_orm, address_update)
        return AddressDto.model_validate(address_orm_update)
