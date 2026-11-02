from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.address.repository import AddressRepository
from app.api.v1.address.schemas import (
    AddressCreate,
    AddressDto,
    AddressUpdate,
    MexicanState,
    PaginatedAddresses,
    normalize_text,
)
from app.models import AddressORM


class AddressService:

    def __init__(self, repo: AddressRepository, db: Session):
        self._repo = repo
        self._db = db

    def create_address(self, receiver_id: int, address_create: AddressCreate) -> AddressDto:
        self._require_receiver(receiver_id)
        self._reject_duplicate(receiver_id, address_create)

        created = self._repo.create(
            self._to_address_orm(address_create, receiver_id)
        )
        return self._commit(created)

    def _require_receiver(self, receiver_id: int) -> None:
        if self._repo.receiver_exists(receiver_id):
            return

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destinatario con id {receiver_id} no existe",
        )

    def _reject_duplicate(self,
                          receiver_id: int,
                          address_create: AddressCreate) -> None:
        addresses = self._repo.list_by_receiver(receiver_id)

        for address in addresses:
            if self._same_address(address, address_create):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "msg": "El destinatario ya tiene un domicilio equivalente",
                        "address_id": address.id,
                    },
                )

    def list_addresses(
        self,
        search: str | None,
        state: MexicanState | None,
        page: int,
        page_size: int,
        order_by: Literal["id", "state"],
        direction: Literal["asc", "desc"],
    ) -> PaginatedAddresses:
        normalized_search = search.strip().upper() if search else None
        normalized_state = state.value if state else None

        totals, addresses = self._repo.get_addresses(
            search=normalized_search,
            state=normalized_state,
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

        return PaginatedAddresses(
            page=current_page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            order_by=order_by,
            direction=direction,
            search=search,
            state=state,
            items=[
                AddressDto.model_validate(address, from_attributes=True)
                for address in addresses
            ],
        )

    def update_address(
        self,
        address_update: AddressUpdate,
        address_id: int,
    ) -> AddressDto:
        address = self._repo.find_by_id(address_id)
        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Domicilio con id {address_id} no existe",
            )

        updated = self._repo.update(address, address_update)
        return self._commit(updated)


    def create_address_with_receiver(
            self, address_create: AddressCreate
    ) -> AddressORM:
        # El destinatario asigna receiver_id al hacer append, en su transacción.
        return self._to_address_orm(address_create)

    def _commit(self, address: AddressORM) -> AddressDto:
        try:
            self._db.commit()
            self._db.refresh(address)
            return AddressDto.model_validate(address)
        except SQLAlchemyError:
            self._db.rollback()
            raise

    @staticmethod
    def _to_address_orm(
            address: AddressCreate, receiver_id: int | None = None
    ) -> AddressORM:
        return AddressORM(
        street = address.street,
        num_street = address.num_street,
        colony = address.colony,
        municipality = address.municipality,
        city = address.city,
        state = address.state,
        postal_code = address.postal_code,
        country = address.country,
        address_reference = address.address_reference,
        receiver_id=receiver_id,
)


    def _same_address(self, current: AddressORM, incoming: AddressCreate) -> bool:
        return self._address_key(current) == self._address_key(incoming)

    @staticmethod
    def _address_key(
            address: AddressORM | AddressCreate
    ) -> tuple[str, str, str, str, str, str, str]:
        # Número de calle y referencia no identifican el domicilio.
        return (
            normalize_text(address.street),
            normalize_text(address.colony),
            normalize_text(address.postal_code),
            normalize_text(address.municipality),
            normalize_text(address.city),
            normalize_text(address.state),
            normalize_text(address.country),
        )
