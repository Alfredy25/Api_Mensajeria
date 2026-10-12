from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal

# Repositories
from app.api.v1.title.repository import TitleRepositoryImpl, TitleRepository
from app.api.v1.job_role.repository import JobRepositoryImpl, JobRoleRepository
from app.api.v1.organization.repository import OrganizationRepositoryImpl, OrganizationRepository
from app.api.v1.position.repository import PositionRepositoryImpl, PositionRepository
from app.api.v1.volante.repository import VolanteRepositoryImpl, VolanteRepository
from app.api.v1.address.repository import AddressRepositoryImpl, AddressRepository
from app.api.v1.contact.repository import ContactRepositoryImpl, ContactRepository
from app.api.v1.receiver.repository import ReceiverRepositoryImpl, ReceiverRepository

# Services
from app.api.v1.title.service import TitleService
from app.api.v1.job_role.service import JobService
from app.api.v1.organization.service import OrganizationService
from app.api.v1.position.service import PositionService
from app.api.v1.volante.service import VolanteService
from app.api.v1.address.service import AddressService
from app.api.v1.contact.service import ContactService
from app.api.v1.receiver.service import ReceiverService


# ------------------------------------------------------------------
# Sesión de base de datos
# ------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------
# Repositories
# ------------------------------------------------------------------

def get_title_repository(db: Session = Depends(get_db)) -> TitleRepository:
    return TitleRepositoryImpl(db=db)


def get_job_role_repository(db: Session = Depends(get_db)) -> JobRoleRepository:
    return JobRepositoryImpl(db=db)


def get_organization_repository(db: Session = Depends(get_db)) -> OrganizationRepository:
    return OrganizationRepositoryImpl(db=db)


def get_position_repository(db: Session = Depends(get_db)) -> PositionRepository:
    return PositionRepositoryImpl(db=db)


def get_volante_repository(db: Session = Depends(get_db)) -> VolanteRepository:
    return VolanteRepositoryImpl(db=db)


def get_address_repository(db: Session = Depends(get_db)) -> AddressRepository:
    return AddressRepositoryImpl(db=db)


def get_contact_repository(db: Session = Depends(get_db)) -> ContactRepository:
    return ContactRepositoryImpl(db=db)


def get_receiver_repository(db: Session = Depends(get_db)) -> ReceiverRepository:
    return ReceiverRepositoryImpl(db=db)


# ------------------------------------------------------------------
# Services
# ------------------------------------------------------------------

def get_title_service(
    db: Session = Depends(get_db),
    repo: TitleRepository = Depends(get_title_repository),
) -> TitleService:
    return TitleService(db=db, repo=repo)


def get_job_service(
    db: Session = Depends(get_db),
    repo: JobRoleRepository = Depends(get_job_role_repository),
) -> JobService:
    return JobService(db=db, repo=repo)


def get_organization_service(
    db: Session = Depends(get_db),
    repo: OrganizationRepository = Depends(get_organization_repository),
) -> OrganizationService:
    return OrganizationService(db=db, repo=repo)


def get_position_service(
    db: Session = Depends(get_db),
    repo: PositionRepository = Depends(get_position_repository),
    repo_job: JobRoleRepository = Depends(get_job_role_repository),
    repo_org: OrganizationRepository = Depends(get_organization_repository),
) -> PositionService:
    return PositionService(db=db, repo=repo, repo_job=repo_job, repo_org=repo_org)


def get_volante_service(
    db: Session = Depends(get_db),
    repo: VolanteRepository = Depends(get_volante_repository),
) -> VolanteService:
    return VolanteService(db=db, repo=repo)


def get_address_service(
    db: Session = Depends(get_db),
    repo: AddressRepository = Depends(get_address_repository),
) -> AddressService:
    return AddressService(repo=repo, db=db)


def get_contact_service(
    db: Session = Depends(get_db),
    repo: ContactRepository = Depends(get_contact_repository),
) -> ContactService:
    return ContactService(db=db, repo=repo)


def get_receiver_service(
    db: Session = Depends(get_db),
    repo: ReceiverRepository = Depends(get_receiver_repository),
    title_service: TitleService = Depends(get_title_service),
    job_service: JobService = Depends(get_job_service),
    org_service: OrganizationService = Depends(get_organization_service),
    position_service: PositionService = Depends(get_position_service),
    volante_service: VolanteService = Depends(get_volante_service),
    address_service: AddressService = Depends(get_address_service),
    contact_service: ContactService = Depends(get_contact_service),
) -> ReceiverService:
    return ReceiverService(
        db=db,
        repo=repo,
        title_service=title_service,
        job_service=job_service,
        org_service=org_service,
        position_service=position_service,
        volante_service=volante_service,
        address_service=address_service,
        contact_service=contact_service,
    )
