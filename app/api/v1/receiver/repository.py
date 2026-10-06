from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models import ReceiverORM, TitleORM, JobRoleORM, OrganizationORM, PositionORM, EntidadesEnum


class ReceiverRepository(ABC):

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[List[ReceiverORM]]:
        ...

    @abstractmethod
    def create(self, tipo_entidad: EntidadesEnum, full_name: str, email: str,
               titulo: TitleORM, puesto: PositionORM) -> ReceiverORM:
        ...

    @abstractmethod
    def update(self, receiver: ReceiverORM, updates: dict) -> ReceiverORM:
        ...

    @abstractmethod
    def find_by_id(self, receiver_id: int) -> Optional[ReceiverORM]:
        ...

class ReceiverRepositoryImpl(ReceiverRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_name(self, full_name: str) -> Optional[List[ReceiverORM]]:
        stmt = (
            select(ReceiverORM)
            .options(
                selectinload(ReceiverORM.addresses),
                joinedload(ReceiverORM.titulo),
                joinedload(ReceiverORM.position),
                selectinload(ReceiverORM.contacts)
            )
            .where(
                func.upper(ReceiverORM.full_name).like(f"%{full_name}%")
            )
        )
        return list(self._db.scalars(stmt).all())

    def create(self, tipo_entity: EntidadesEnum, full_name: str, email: str,
               titulo: TitleORM, puesto: PositionORM ) -> ReceiverORM:
        receiver = ReceiverORM(
            titulo=titulo,
            tipo_entity=tipo_entity.value,
            full_name=full_name,
            email=email,
            position=puesto
        )
        self._db.add(receiver)
        self._db.flush()
        return receiver


    def find_by_id(self, receiver_id: int) -> Optional[ReceiverORM]:
        return self._db.get(ReceiverORM, receiver_id)

    def update(self, receiver: ReceiverORM, updates: dict) -> ReceiverORM:
        for attr, value in updates.items():
            setattr(receiver, attr, value)
        return receiver