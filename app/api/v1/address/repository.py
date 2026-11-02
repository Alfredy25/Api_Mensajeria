from abc import ABC, abstractmethod
from math import ceil

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.api.v1.address.schemas import AddressUpdate, TotalsAddresses
from app.models import AddressORM, ReceiverORM


class AddressRepository(ABC):

    @abstractmethod
    def create(self, new_address: AddressORM) -> AddressORM:
        ...

    @abstractmethod
    def update(
        self,
        address: AddressORM,
        address_update: AddressUpdate,
    ) -> AddressORM:
        ...

    @abstractmethod
    def find_by_id(self, address_id: int) -> AddressORM | None:
        ...

    @abstractmethod
    def receiver_exists(self, receiver_id: int) -> bool:
        ...

    @abstractmethod
    def list_by_receiver(self, receiver_id: int) -> list[AddressORM]:
        ...

    @abstractmethod
    def get_addresses(
        self,
        search: str | None,
        state: str | None,
        page: int,
        page_size: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsAddresses, list[AddressORM]]:
        ...


class AddressRepositoryImpl(AddressRepository):

    def __init__(self, db: Session):
        self._db = db

    def create(self, new_address: AddressORM) -> AddressORM:
        self._db.add(new_address)
        self._db.flush()
        return new_address

    def find_by_id(self, address_id: int) -> AddressORM | None:
        return self._db.get(AddressORM, address_id)

    def receiver_exists(self, receiver_id: int) -> bool:
        # Session.get carga título, puesto, domicilios y contactos.
        stmt = select(ReceiverORM.id).where(ReceiverORM.id == receiver_id)
        receiver_find = self._db.scalar(stmt)
        return receiver_find is not None

    def list_by_receiver(self, receiver_id: int) -> list[AddressORM]:
        stmt = select(AddressORM).where(AddressORM.receiver_id == receiver_id)
        return list(self._db.scalars(stmt).all())

    def update(self, address: AddressORM, address_update: AddressUpdate) -> AddressORM:
        updates = address_update.model_dump(exclude_unset=True, mode="json")

        for field_name, value in updates.items():
            setattr(address, field_name, value)

        return address

    def get_addresses(self,
                      search: str | None,
                      state: str | None,
                      page: int,
                      page_size: int,
                      order_by: str,
                      direction: str,
    ) -> tuple[TotalsAddresses, list[AddressORM]]:
        stmt = self._apply_filters(select(AddressORM), search, state)
        total = self._count(search, state)
        totals = self._calculate_totals(total, page_size, page)
        offset = totals.offset

        stmt = self._apply_order(stmt, order_by, direction)
        addresses = list(
            self._db.scalars(
                stmt.offset(offset).limit(page_size)
            ).all()
        )
        return totals, addresses

    def _count(self, search: str | None, state: str | None) -> int:
        stmt = self._apply_filters(
            select(func.count()).select_from(AddressORM),
            search,
            state,
        )
        return self._db.scalar(stmt) or 0

    @staticmethod
    def _apply_filters(
        stmt: Select,
        search: str | None,
        state: str | None,
    ) -> Select:
        if search:
            term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.upper(AddressORM.colony).like(term),
                    func.upper(AddressORM.street).like(term),
                    func.upper(AddressORM.city).like(term),
                    func.upper(AddressORM.municipality).like(term),
                )
            )

        if state:
            stmt = stmt.where(AddressORM.state == state)

        return stmt

    @staticmethod
    def _calculate_totals(
        total: int,
        page_size: int,
        page: int,
    ) -> TotalsAddresses:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size

        return TotalsAddresses(
            total=total,
            total_pages=total_pages,
            current_page=current_page,
            offset=offset,
        )

    @staticmethod
    def _apply_order(stmt: Select, order_by: str, direction: str) -> Select:
        if order_by == "state":
            column = AddressORM.state
        else:
            column = AddressORM.id

        if direction == "asc":
            return stmt.order_by(column.asc())

        return stmt.order_by(column.desc())


