from datetime import timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from zoneinfo import ZoneInfo
from app.core.db import Base, engine, SessionLocal
from app.models import (ReceiverORM, JobRoleORM, TitleORM, PositionORM,
                        OrganizationORM, AddressORM, EntidadesEnum, ContactORM,
                        VolanteORM)

from app.models import UserORM, users_roles, RoleORM, NameRole, RegisterORM, Sede

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        try:
            # Reutilizamos el titulo que ya existe en la BD
            titulo = session.execute(
                select(TitleORM).where(TitleORM.abreviatura == "C.P.")
            ).scalar_one_or_none()

            # Cargo y dependencia nuevos (gubernamentales)
            cargo_tesorero = JobRoleORM(
                abreviatura="PDTE. DE LA MESA DIRECTIVA",
                significado="Presidente de la Mesa Directiva"
            )
            municipio_durango_capital = OrganizationORM(
                name="CONGRESO DEL ESTADO DE TABASCO",
                state="TABASCO"
            )

            # Puesto nuevo (cargo + dependencia)
            puesto_tesoreria = PositionORM(
                job_role=cargo_tesorero,
                organization=municipio_durango_capital
            )

            # Destinatario nuevo, mismo titulo
            destinatario = ReceiverORM(
                tipo_entidad=EntidadesEnum.PERSONA,
                full_name="JORGE ALBERTO CASTILLO REYES",
                email="mesa_directiva_pdte@durango.gob.mx",
                titulo=titulo,
                position=puesto_tesoreria
            )

            # Domicilio diferente
            domicilio = AddressORM(
                street="CALLE 5 DE FEBRERO",
                num_street="800",
                colony="ZONA CENTRO",
                state="TABASCO",
                postal_code="34000",
                city="TABASCO",
                country="MEXICO",
                address_reference="PALACIO MUNICIPAL, TESORERIA"
            )
            destinatario.addresses.append(domicilio)

            # Contacto diferente
            contacto = ContactORM(
                phone="6181375000",
                ext="2401"
            )
            destinatario.contacts.append(contacto)

            session.add(destinatario)
            session.commit()
            session.refresh(destinatario)

            print(
                f"destinatario: {destinatario.id} {destinatario.titulo.abreviatura} {destinatario.full_name}"
                f"\ncargo: {destinatario.position.job_role.abreviatura}"
                f"\ndependencia: {destinatario.position.organization.name}"
                f"\ndomicilio: {domicilio.street} {domicilio.num_street}, {domicilio.colony}, {domicilio.city}"
                f"\ncontacto: {contacto.phone} ext. {contacto.ext}"
            )

        except SQLAlchemyError as e:
            session.rollback()
            print(e)
            print(e.code)
            print(e.args[0])
            print(e.__class__.__name__)

            # Titulo
            # titulo = TitleORM(
            #     abreviatura="C.P.",
            #     significado="Contador Público o Contadora Pública"
            # )
            #
            # # Cargo y dependencia
            # cargo_presidente = JobRoleORM(
            #     abreviatura="PDTE. MUNICIPAL",
            #     significado="Presidente Municipal"
            # )
            # municipio_durango = OrganizationORM(
            #     name="MUNICIPIO DE PUEBLO NUEVO",
            #     state="DURANGO"
            # )
            #
            # # Puesto (cargo + dependencia)
            # puesto_durango = PositionORM(
            #     job_role=cargo_presidente,
            #     organization=municipio_durango
            # )
            #
            # # Destinatario
            # destinatario = ReceiverORM(
            #     tipo_entidad=EntidadesEnum.PERSONA,
            #     full_name="ADAIR HERNANDEZ MARTINEZ",
            #     email="presidencia@pueblonuevo.gob.mx",
            #     titulo=titulo,
            #     position=puesto_durango
            # )
            #
            # # Domicilio
            # domicilio = AddressORM(
            #     street="C. AV. CHIAPAS",
            #     num_street="514",
            #     colony="RAMON FARIAS",
            #     state="DURANGO",
            #     postal_code="34950",
            #     city="PUEBLO NUEVO",
            #     country="MEXICO",
            #     address_reference="PRESIDENCIA MUNICIPAL"
            # )
            # destinatario.addresses.append(domicilio)
            #
            # # Contacto
            # contacto = ContactORM(
            #     phone="6181234567",
            #     ext="101"
            # )
            # destinatario.contacts.append(contacto)
            #
            # # Volante
            # volante = VolanteORM(name="VOLANTE-2026-0001")
            # destinatario.volantes.append(volante)
            #
            # session.add(destinatario)
            # session.commit()
            # session.refresh(destinatario)
            #
            # print(
            #     f"destinatario: {destinatario.id} {destinatario.titulo.abreviatura} {destinatario.full_name}"
            #     f"\ncargo: {destinatario.position.job_role.abreviatura}"
            #     f"\ndependencia: {destinatario.position.organization.name}"
            #     f"\ndomicilio: {domicilio.street} {domicilio.num_street}, {domicilio.colony}, {domicilio.city}"
            #     f"\ncontacto: {contacto.phone} ext. {contacto.ext}"
            #     f"\nvolante: {volante.name}"
            #     f"\ncreado en: {destinatario.created_at}"
            # )