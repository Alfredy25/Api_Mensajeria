from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.sql.operators import and_

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
    def ensure_title(self, abreviatura: str, significado: str) -> TitleORM:
        ...

    @abstractmethod
    def ensure_puesto(self, cargo: JobRoleORM, organization: OrganizationORM) -> PositionORM:
        ...

    @abstractmethod
    def ensure_cargo(self, abreviatura: str, significado: str) -> JobRoleORM:
        ...

    @abstractmethod
    def ensure_organization(self, name: str, state: str) -> OrganizationORM:
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

    def create(self, tipo_entidad: EntidadesEnum, full_name: str, email: str,
               titulo: TitleORM, puesto: PositionORM ) -> ReceiverORM:
        receiver = ReceiverORM(
            tipo_entidad=tipo_entidad.value,
            full_name=full_name,
            email=email,
            position=puesto
        )
        self._db.add(receiver)
        self._db.flush()
        return receiver

    def ensure_cargo(self, abreviatura: str, significado: str) -> JobRoleORM:
        cargo_obj = self._db.execute(
            select(JobRoleORM).where(
                JobRoleORM.abreviatura == func.upper(abreviatura)
            )
        ).scalar_one_or_none()
        if cargo_obj:
            return cargo_obj

        cargo_obj = JobRoleORM(abreviatura=abreviatura, significado=significado)
        self._db.add(cargo_obj)
        self._db.flush()
        return cargo_obj

    def ensure_organization(self, name: str, state: str) -> OrganizationORM:
        organization_obj = self._db.execute(
            select(OrganizationORM).where(
                and_(
                    OrganizationORM.name == name,
                    OrganizationORM.state == state
                )
            )
        ).scalar_one_or_none()

        if organization_obj:
            return organization_obj

        organization_obj = OrganizationORM(name=name, state=state)
        self._db.add(organization_obj)
        self._db.flush()
        return organization_obj

    def ensure_puesto(self, cargo: JobRoleORM, organization: OrganizationORM) -> PositionORM:
        puesto_obj = self._db.execute(
            select(PositionORM).where(
                and_(
                    PositionORM.job_id == cargo.id,
                    PositionORM.organization_id == organization.id
                )
            )
        ).scalar_one_or_none()
        if puesto_obj:
            return puesto_obj

        puesto_obj= PositionORM(job_role=cargo, organization=organization)
        self._db.add(puesto_obj)
        self._db.flush()
        return puesto_obj

    def ensure_title(self, abreviatura: str, significado: str) -> TitleORM:
        title_obj = self._db.execute(
            select(TitleORM).where(
                TitleORM.abreviatura == func.upper(abreviatura)
            )
        ).scalar_one_or_none()
        if title_obj:
            return title_obj
        title_obj = TitleORM(name=abreviatura, significado=significado)
        self._db.add(title_obj)
        self._db.flush()
        return title_obj

    def find_by_id(self, receiver_id: int) -> Optional[ReceiverORM]:
        return self._db.get(ReceiverORM, receiver_id)

    def update(self, receiver: ReceiverORM, updates: dict) -> ReceiverORM:
        for attr, value in updates.items():
            setattr(receiver, attr, value)
        return receiver