from datetime import timezone

from sqlalchemy.exc import SQLAlchemyError
from zoneinfo import ZoneInfo
from app.core.db import Base, engine, SessionLocal
from app.models import (ReceiverORM, JobRoleORM, TitleORM, PositionORM,
                        OrganizationORM, AddressORM, EntidadesEnum, ContactORM)

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        try:
            # buscamos al destinatario
            dest = session.get(ReceiverORM, 1)
            print(f"Destinatario: {dest.full_name}")
            print(f"Puesto actual: {dest.position.job_role.significado} en {dest.position.organization.name}")

            for idx, address in enumerate(dest.addresses):
                print(f'direccion {idx}')
                print(address.street)
                print(address.num_street)
                print(address.city)
                print(address.state)
                print(address.postal_code)
                # print(address.extras)
            # session.delete(dest)
            # session.commit()

            # print(destinatario)
            # print(f"destinatario nombre: {destinatario.titulo.abreviatura} {destinatario.full_name}"
            #       f"\ncargo: {destinatario.position.job_role.abreviatura}\nDependencia: {destinatario.position.organization.name}")

            # Creamos o buscamos el cargo y la organización
            # cargo_presidente = session.get(JobRoleORM, 1)
            # municipio_durango = session.get(OrganizationORM, 1)
            # cargo_presidente = JobRoleORM(abreviatura="PDTE. MUNICIPAL", significado="Presidente Municipal")
            # municipio_durango = OrganizationORM(name="MUNICIPIO DE PUEBLO NUEVO", state="DURANGO")
            # # #
            # # # # Creamos la posicion
            # puesto_durango = session.get(PositionORM, 1)
            # # # puesto_durango = PositionORM(job_role=cargo_presidente, organization=municipio_durango)
            # # # #
            # # # # # Creamos el destinatario
            # title = session.get(TitleORM, 1)
            # # # title_1 = TitleORM(abreviatura="C.P.", significado="Contador Público o Contadora Pública")
            # # # #
            # destinatario1 = ReceiverORM(
            #     tipo_entidad=EntidadesEnum.PERSONA,
            #     full_name="ADAIR HERNANDEZ MARTINEZ",
            #     titulo=title,
            #     position=puesto_durango
            # )
            # session.add(destinatario1)

            # session.commit()
            #
            # direccion2 = AddressORM(
            #     street="C. AV. CHIAPAS",
            #     num_street="514",
            #     colony="RAMON FARIAS",
            #     state="MICHOACAN",
            #     postal_code="58000",
            #     city="URUAPAN",
            #     country="MEXICO",
            #     address_reference="PRESIDENCIA MUNICIPAL",
            #     extras="ENTREGAR EN OFICIALIA DE PARTES O RECEPCION EN UN HORARIO DE 09:00 A 14:00 HRS."
            # )
            # dest.addresses.append(direccion2)
            # session.add(dest)
            # session.commit()
            # destinatario1.addresses.append(direccion1)
            # session.add(destinatario1)
            # # # destinatario2 = ReceiverORM(tipo_entidad=EntidadesEnum.PERSONA, full_name="ACASIO FLORES GUERRERO", titulo=title_1)
            # session.add_all([cargo_presidente, municipio_durango, puesto_durango, title_1, destinatario1])
            # session.commit()
            # session.refresh(destinatario1)
            # print(f"destinatario nombre: {destinatario1.id} {destinatario1.titulo.abreviatura} {destinatario1.full_name}"
            #       f"\ncargo: {destinatario1.position.job_role.abreviatura}\nDependencia: {destinatario1.position.organization.name}"
            #       f"\ncreado en: {destinatario1.created_at.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo('America/Mexico_City'))}")
            # session.commit()

        except SQLAlchemyError as e:
            session.rollback()
            print(e)
            print(e.code)
            print(e.args[0])
            print(e.__class__.__name__)
