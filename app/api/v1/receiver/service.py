from math import ceil
from typing import Optional, Literal, List

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload, joinedload

from app.api.v1.address.service import AddressService
from app.api.v1.contact.service import ContactService
from app.api.v1.job_role.schemas import JobCreate
from app.api.v1.job_role.service import JobService
from app.api.v1.organization.schemas import OrganizationCreate
from app.api.v1.organization.service import OrganizationService
from app.api.v1.position.service import PositionService
from app.api.v1.receiver.repository import ReceiverRepository
from app.api.v1.receiver.schemas import ReceiverCreate, ReceiverDto, PaginatedReceiver
from app.api.v1.title.service import TitleService
from app.api.v1.volante.service import VolanteService
from app.models import EntidadesEnum, TitleORM, PositionORM, ReceiverORM, AddressORM

# Cargos genéricos reutilizables por tipo de destinatario
SIN_CARGO = JobCreate(
    abbreviation="SIN CARGO",
    meaning="Sin cargo especificado",
)
INSTITUCIONAL_GOBIERNO = JobCreate(
    abbreviation="INSTITUCIONAL GOBIERNO",
    meaning="Destinatario dirigido a institución gubernamental",
)
INSTITUCIONAL_PRIVADO = JobCreate(
    abbreviation="INSTITUCIONAL PRIVADO",
    meaning="Destinatario dirigido a institución privada",
)

# from enum import StrEnum
#
#
# class Estates(str, StrEnum):
#     CIUDAD_DE_MEXICO = "CIUDAD DE MÉXICO"
#     AGUASCALIENTES = "AGUASCALIENTES"
#     COAHUILA = "COAHUILA"
#     BAJA_CALIFORNIA = "BAJA CALIFORNIA"
#     BAJA_CALIFORNIA_SUR = "BAJA CALIFORNIA SUR"
#     CAMPECHE = "CAMPECHE"
#     COLIMA = "COLIMA"
#     CHIAPAS = "CHIAPAS"
#     CHIHUAHUA = "CHIHUAHUA"
#     DURANGO = "DURANGO"
#     GUANAJUATO = "GUANAJUATO"
#     GUERRERO = "GUERRERO"
#     HIDALGO = "HIDALGO"
#     JALISCO = "JALISCO"
#     ESTADO_DE_MEXICO = "ESTADO DE MÉXICO"
#     MICHOACAN = "MICHOACÁN"
#     MORELOS = "MORELOS"
#     NAYARIT = "NAYARIT"
#     NUEVO_LEON = "NUEVO LEÓN"
#     OAXACA = "OAXACA"
#     PUEBLA = "PUEBLA"
#     QUERETARO = "QUERÉTARO"
#     QUINTANA_ROO = "QUINTANA ROO"
#     SAN_LUIS_POTOSI = "SAN LUIS POTOSÍ"
#     SINALOA = "SINALOA"
#     SONORA = "SONORA"
#     TABASCO = "TABASCO"
#     TAMAULIPAS = "TAMAULIPAS"
#     TLAXCALA = "TLAXCALA"
#     VERACRUZ = "VERACRUZ"
#     YUCATAN = "YUCATÁN"
#     ZACATECAS = "ZACATECAS"



class ReceiverService:

    def __init__(self, db: Session, repo: ReceiverRepository,
                 title_service: TitleService,
                 job_service: JobService,
                 org_service: OrganizationService,
                 position_service: PositionService,
                 volante_service: VolanteService,
                 address_service: AddressService,
                 contact_service: ContactService):
        self._db = db
        self._repo = repo
        self._title_service = title_service
        self._job_service = job_service
        self._org_service = org_service
        self._position_service = position_service
        self._volante_service = volante_service
        self._address_service = address_service
        self._contact_service = contact_service

    def create_receiver(self, payload: ReceiverCreate) -> ReceiverDto:
        """Orquesta el alta completa de un destinatario en una sola transacción."""
        try:
            title_orm, position_orm = self._resolve_title_and_position(payload)
            full_name = self._normalize_full_name(payload.full_name)
            email = self._normalize_email(payload.email)

            self._check_duplicate(
                type_entity=payload.type_entity,
                full_name=full_name,
                position_id=position_orm.id if position_orm else None,
            )

            # Crear destinatario si no hay duplicados
            receiver_orm = self._repo.create(
                type_entity=payload.type_entity, full_name=full_name,
                email=email, title=title_orm, position=position_orm
            )

            # Dirección obligatoria
            address_orm = self._address_service.create_address_with_receiver(
                address_create=payload.address,
            )
            receiver_orm.addresses.append(address_orm)

            # Contacto opcional
            if payload.contact:
                contact_orm = self._contact_service.create_contact_with_receiver(
                    contact=payload.contact
                )
                receiver_orm.contacts.append(contact_orm)

            # Volante opcional
            if payload.volante:
                volante_orm = self._volante_service.ensure_volante(
                    volante=payload.volante,
                )
                receiver_orm.volantes.append(volante_orm)

            self._db.commit()
            self._db.refresh(receiver_orm)

            return ReceiverDto.model_validate(receiver_orm, from_attributes=True)

        except HTTPException:
            self._db.rollback()
            raise
        except SQLAlchemyError:
            self._db.rollback()
            raise


    def list_receivers(self, query: str | None,
                       page_size: int,
                       page: int,
                       order_by: str,
                       direction: str,
                       type_entity: str | None = None,
                       state: str | None = None
                       ) -> PaginatedReceiver:

        results = select(ReceiverORM).options(
            selectinload(ReceiverORM.addresses),
            joinedload(ReceiverORM.title),
            joinedload(ReceiverORM.position).joinedload(PositionORM.job_role),
            joinedload(ReceiverORM.position).joinedload(PositionORM.organization),
            selectinload(ReceiverORM.contacts),
        )
        state_org = None
        filters = []
        if query:
            query = query.upper().strip()
            filters.append(func.upper(ReceiverORM.full_name).like(f"%{query}%"))
        if type_entity:
            filters.append(ReceiverORM.type_entity == type_entity)
        if state:
            normalized_state = state.strip().upper()
            filters.append(
                (select(AddressORM.id).where(
                    and_(AddressORM.receiver_id == ReceiverORM.id,
                         func.upper(AddressORM.state) == normalized_state
                         )
                ).exists())
            )
            state_org = ReceiverORM.position.organization.state == state

        if state_org:
            results = select(ReceiverORM).where(
                or_(
                    and_(*filters),
                    state_org
                )
            )
        else:
            results = select(ReceiverORM).where(
                and_(
                    *filters
                )
            )

        total = self._db.scalar(
            select(
                func.count()
            ).select_from(results.subquery())
        ) or 0

        total_pages = ceil(total / page_size) if total > 0 else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)

        if order_by == "id":
            order_col = ReceiverORM.id
        elif order_by == "full_name":
            order_col = func.lower(ReceiverORM.full_name)
        elif order_by == "name_org":
            order_col = ReceiverORM.position.organization.name
        else:
            order_col = ReceiverORM.addresses.state

        results = results.order_by(
            order_col.asc() if direction == "asc" else order_col.desc()
        )

        if total_pages == 0:
            items: List[ReceiverORM] = []
        else:
            start =(current_page - 1) * page_size
            items: List[ReceiverORM] = list(
                self._db.scalars(
                    results.limit(page_size).offset(start)
                ).all()
            )
        has_prev = current_page > 1
        has_next = current_page < total_pages if total_pages > 0 else False

        return PaginatedReceiver(
            page=page,
            page_size=page_size,
            total = total,
            total_pages = total_pages,
            has_prev = has_prev,
            has_next = has_next,
            order_by = order_by,
            direction = direction,
            search=query,
            items=[ReceiverDto.model_validate(receiver) for receiver in items],
        )















    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _resolve_title_and_position(self, payload: ReceiverCreate)\
            -> tuple[TitleORM | None, PositionORM | None]:
        """Resuelve título y puesto según el tipo de destinatario."""
        if payload.type_entity == EntidadesEnum.PERSONA:
            return self._resolve_persona(payload)
        return self._resolve_institution(payload)

    def _resolve_persona(self, payload: ReceiverCreate)\
            -> tuple[TitleORM, PositionORM | None]:
        """PERSONA: título obligatorio, puesto según datos recibidos."""
        title_orm = self._title_service.ensure_title(
            title=payload.title,
        )

        if payload.position is None:
            return title_orm, None

        job_create = payload.position.job_role if payload.position.job_role else SIN_CARGO
        position_orm = self._ensure_position_from_parts(
            job_create=job_create,
            org_create=payload.position.organization,
        )
        return title_orm, position_orm

    def _resolve_institution(self, payload: ReceiverCreate
    ) -> tuple[None, PositionORM]:
        """GOBIERNO / PRIVADA: sin título, puesto obligatorio."""
        if payload.position.job_role:
            job_create = payload.position.job_role
        elif payload.type_entity == EntidadesEnum.GOBIERNO:
            job_create = INSTITUCIONAL_GOBIERNO
        else:
            job_create = INSTITUCIONAL_PRIVADO

        position_orm = self._ensure_position_from_parts(
            job_create=job_create,
            org_create=payload.position.organization,
        )
        return None, position_orm

    def _ensure_position_from_parts(self, job_create: JobCreate,
                                    org_create: OrganizationCreate) -> PositionORM:
        """Busca o crea cargo, organización y puesto."""
        job_orm = self._job_service.ensure_job_role(job=job_create)
        org_orm = self._org_service.ensure_organization(org_create=org_create)
        return self._position_service.ensure_position(
            job=job_orm, organization=org_orm,
        )

    def _check_duplicate(self, type_entity: EntidadesEnum, full_name: str | None,
                         position_id: int | None) -> None:
        """Lanza 409 si ya existe un destinatario con la misma identidad lógica."""
        existing = self._repo.find_duplicate(
            type_entity=type_entity,
            full_name=full_name,
            position_id=position_id,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"msg":"El destinatario ya existe", "receiver_id": existing.id},
            )

    @staticmethod
    def _normalize_full_name(full_name: str | None) -> str | None:
        """Elimina espacios exteriores y convierte a mayúsculas."""
        if full_name is None:
            return None
        return full_name.strip().upper()

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        """Elimina espacios exteriores y convierte a minúsculas."""
        if email is None:
            return None
        return str(email).strip().lower()
