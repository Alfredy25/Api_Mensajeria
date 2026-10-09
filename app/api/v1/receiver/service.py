from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.address.service import AddressService
from app.api.v1.contact.service import ContactService
from app.api.v1.job_role.schemas import JobCreate
from app.api.v1.job_role.service import JobService
from app.api.v1.organization.service import OrganizationService
from app.api.v1.position.service import PositionService
from app.api.v1.receiver.repository import ReceiverRepository
from app.api.v1.receiver.schemas import ReceiverCreate, ReceiverDto
from app.api.v1.title.service import TitleService
from app.api.v1.volante.service import VolanteService
from app.models import EntidadesEnum


class ReceiverService:
    def __init__(self, repo: ReceiverRepository, db: Session,
                 service_position: PositionService, service_title: TitleService,
                 service_volante: VolanteService, service_job: JobService,
                 service_org: OrganizationService, address_service: AddressService,
                 contact_service: ContactService):
        self._db = db
        self._repo = repo
        self._service_position = service_position
        self._service_title = service_title
        self._service_volante = service_volante
        self._service_job = service_job
        self._service_org = service_org
        self._address_service = address_service
        self._contact_service = contact_service
        self.sin_cargo = {
            "persona": {"abbreviation":"SIN CARGO",
                        "meaning": "Destinatario con cargo desconocido"},
            "gobierno": {"abbreviation":"INSTITUCIONAL Gobierno",
                        "meaning": "Destinatario dirigido a institución"},
            "privada": {"abbreviation":"INSTITUCIONAL PRIVADO",
                        "meaning": "Destinatario dirigido a institución"},
        }

    def create_receiver(self, receiver: ReceiverCreate) -> ReceiverDto:
        if receiver.type_entity == EntidadesEnum.PERSONA:
            if receiver.position.job_role and not receiver.position.organization:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede crear un destinatario de tipo persona con cargo pero sin dependencia"
                )
            job_role_orm = self._service_job.ensure_job_role(
                job=receiver.position.job_role if receiver.position.job_role
                else self.sin_cargo.get("persona")
            )
            org_orm = self._service_org.ensure_organization(
                org_create=receiver.position.organization,
            )
            position_orm = self._service_position.ensure_position(
                job=job_role_orm, organization=org_orm
            )
            title_orm = self._service_title.ensure_title(
                abbreviation=receiver.title.abbreviation,
                meaning=receiver.title.meaning
            )
            receiver_orm = self._repo.create(
                type_entity=receiver.type_entity,
                full_name=receiver.full_name,
                email=str(receiver.email) if receiver.email else None,
                position=position_orm,
                title=title_orm
            )
            address_orm = self._address_service.create_address_with_receiver(
                address_create=receiver.address,
            )
            receiver_orm.addresses.append(address_orm)
            if receiver.volante:
                volante_orm = self._service_volante.ensure_volante(
                    volante = receiver.volante
                )
                receiver_orm.volantes.append(volante_orm)
            if receiver.contact:
                contact_orm = self._contact_service.create_contact_with_receiver(
                    contact=receiver.contact
                )
                receiver_orm.contacts.append(contact_orm)
            self._db.commit()
            self._db.refresh(receiver_orm)
            return ReceiverDto.model_validate(
                receiver_orm,
                from_attributes=True
            )

    def find_by_name(self, name: str):
        pass

