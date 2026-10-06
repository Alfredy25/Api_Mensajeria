from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import List, Literal
from sqlalchemy.orm import Session
from app.api.v1.address.repository import AddressRepositoryImpl
from app.models.address import AddressORM
from app.api.v1.receiver.repository import ReceiverRepositoryImpl
from app.api.v1.receiver.schemas import ReceiverDto, ReceiverCreate
from app.api.v1.contact.repository import ContactRepositoryImpl

router = APIRouter(prefix="/receivers", tags=["receivers"])

@router.get("/", response_model=List[ReceiverDto])
def get_receivers(
        type_receiver: Literal["PERSONA", "PRIVADA", "GOBIERNO"] = Query("Persona", description="El tipo de destinatario"),
        name: str = Query(..., examples=["Juan Carlos Garcia"]),
        db: Session = Depends(get_db)
):
    repo = ReceiverRepositoryImpl(db=db)
    if type_receiver == "Persona":
        receivers_orm = repo.find_by_name(full_name=name)
        if not receivers_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existen destinatarios con ese nombre")

        return [ReceiverDto.model_validate(receiver) for receiver in receivers_orm]

    receivers_orm = repo.find_by_dependecy(name=name)
    return receivers_orm

@router.post("/", response_model=ReceiverDto)
def create_receiver(db: Session = Depends(get_db), receiver: ReceiverCreate = Body(...)):
    """Crea un nuevo destinatario con create_receiver del repositorio. pero valida primero
    asegura no duplicados del nombre, email y mismo titulo para no volver a crearlo. y valida si 
    tiene address para crear una direccion y asignarselo al destinatario, revisa si tiene titulo para crearlo si
    no existe, crea un puesto primero la dependencia y luego el cargo y al final el puesto que se 
    asigna al destinatario esto usando el repositorio"""
    receiver_orm = None
    repo_receiver = ReceiverRepositoryImpl(db=db)
    repo_address = AddressRepositoryImpl(db=db)
    repo_contact = ContactRepositoryImpl(db=db)
    job_role_orm = None
    dependencia_orm = None
    title_orm = None
    position_orm = None

    if receiver.title:
        title_abrev = receiver.title.abbreviation
        title_meaning = receiver.title.meaning
        title_orm = repo_receiver.ensure_title(abreviatura=title_abrev, meaning=title_meaning)


    if receiver.position:
        cargo_abrev = receiver.position.job_role.abbreviation
        cargo_meaning = receiver.position.job_role.meaning
        dependencie_name = receiver.position.organization.name
        dependencia_state = receiver.position.organization.state

        job_role_orm = repo_receiver.ensure_cargo(abreviatura=cargo_abrev, meaning=cargo_meaning)
        dependencia_orm = repo_receiver.ensure_organization(nombre=dependencie_name, estado=dependencia_state)

        position_orm = repo_receiver.ensure_position(job_role=job_role_orm, organization=dependencia_orm)

    receiver_orm = repo_receiver.create(
        tipo_entity=receiver.type_entity,
        full_name=receiver.full_name,
        email=receiver.email,
        title=title_orm,
        position=position_orm
        )
    
    if receiver.address:
        address_create = receiver.address
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
        address_orm = repo_address.create(new_address=new_address)
        receiver_orm.address.append(address_orm)
    if receiver.contact:
        contact_create = receiver.contact
        new_contact = ContactORM(phone=contact_create.phone, ext=contact_create.ext)
        contact_orm = repo_contact.create(new_contact=new_contact)
        receiver_orm.contacts.append(contact_orm)

    db.commit()
    db.refresh(receiver_orm)
    
    return ReceiverDto.model_validate(receiver_orm)

