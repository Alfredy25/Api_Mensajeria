from abc import ABC, abstractmethod

from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models import ReceiverORM, TitleORM, PositionORM, EntidadesEnum


class ReceiverRepository(ABC):

    @abstractmethod
    def find_by_name(self, name: str) -> list[ReceiverORM]:
        ...

    @abstractmethod
    def create(
        self,
        type_entity: EntidadesEnum,
        full_name: str | None,
        email: str | None,
        title: TitleORM | None,
        position: PositionORM | None,
    ) -> ReceiverORM:
        ...

    @abstractmethod
    def find_duplicate(self, type_entity: EntidadesEnum, full_name: str | None,
                       position_id: int | None) -> ReceiverORM | None:
        ...

    @abstractmethod
    def update(self, receiver: ReceiverORM, updates: dict) -> ReceiverORM:
        ...

    @abstractmethod
    def find_by_id(self, receiver_id: int) -> ReceiverORM | None:
        ...


class ReceiverRepositoryImpl(ReceiverRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_name(self, full_name: str) -> list[ReceiverORM]:
        stmt = (
            select(ReceiverORM)
            .options(
                selectinload(ReceiverORM.addresses),
                joinedload(ReceiverORM.title),
                joinedload(ReceiverORM.position),
                selectinload(ReceiverORM.contacts),
            )
            .where(func.upper(ReceiverORM.full_name).like(f"%{full_name.upper()}%"))
        )
        return list(self._db.scalars(stmt).all())

    def create(self, type_entity: EntidadesEnum, full_name: str | None,
               email: str | None, title: TitleORM | None,
               position: PositionORM | None) -> ReceiverORM:

        receiver = ReceiverORM(
            type_entity=type_entity,
            full_name=full_name,
            email=email,
            title=title,
            position=position,
        )
        self._db.add(receiver)
        self._db.flush()
        return receiver

    def find_duplicate(self, type_entity: EntidadesEnum,  full_name: str | None
                       , position_id: int | None) -> ReceiverORM | None:
        """Busca un destinatario duplicado según la identidad lógica del tipo."""
        if type_entity == EntidadesEnum.PERSONA:
            return self._find_duplicate_persona(
                full_name=full_name,
                position_id=position_id,
            )
        return self._find_duplicate_institution(
            type_entity=type_entity,
            position_id=position_id,
        )

    def _find_duplicate_persona(self, full_name: str,
                                position_id: int | None) -> ReceiverORM | None:
        """PERSONA: type_entity + full_name(upper) + title_id + position_id."""
        filters = [ReceiverORM.type_entity == EntidadesEnum.PERSONA,
                   func.upper(ReceiverORM.full_name) == full_name.upper()]

        if position_id is not None:
            filters.append(ReceiverORM.position_id == position_id)
        else:
            filters.append(ReceiverORM.position_id.is_(None))

        return self._db.execute(
            select(ReceiverORM).where(
                and_(
                    *filters)
            )
        ).scalar_one_or_none()

    def _find_duplicate_institution(self, type_entity: EntidadesEnum,
                                    position_id: int | None) -> ReceiverORM | None:
        """GOBIERNO / PRIVADA: type_entity + position_id."""
        return self._db.execute(
            select(ReceiverORM).where(
                ReceiverORM.type_entity == type_entity,
                ReceiverORM.position_id == position_id,
            )
        ).scalar_one_or_none()

    def find_by_id(self, receiver_id: int) -> ReceiverORM | None:
        return self._db.get(ReceiverORM, receiver_id)

    def update(self, receiver: ReceiverORM, updates: dict) -> ReceiverORM:
        for attr, value in updates.items():
            setattr(receiver, attr, value)
        return receiver
