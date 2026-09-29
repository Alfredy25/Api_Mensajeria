from sqlalchemy.exc import SQLAlchemyError

from app.models import UserORM, users_roles, RoleORM, NameRole, RegisterORM, Sede
from app.core.db import Base, SessionLocal, engine

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        try:
            user = session.get(UserORM, 1)
            session.delete(user)
            session.commit()
            # role_new_1 = RoleORM(name=NameRole.ADMIN)
            # role_new_2 = RoleORM(name=NameRole.OPERATOR)
            # role_new_3 = RoleORM(name=NameRole.CLIENT)
            #
            # session.add_all([role_new_1, role_new_2, role_new_3])
            # session.flush()
            #
            # user_new = UserORM(name="alfredo", email="alfredo1@gmail.com", password_hash="holamundo123", is_active=True)
            # user_new.roles.extend([role_new_1, role_new_2])
            #
            # register_new = RegisterORM(sede=Sede.AJUSCO, image_name="imagen1",
            #                            raw_receiver="MTRA. MIREYLI MARÍA WILSON ARIAS TITULAR DE LA SECRETARÍA ANTICORRUPCIÓN Y BUEN GOBIERNO DEL ESTADO DE TABASCO. AV. PASEO TABASCO #1504 COL. TABASCO 2000, C.P. 86035 VILAHERMOSA, TABASCO, MÉXICO.",
            #                            full_name="MTRA. MIREYLI MARÍA WILSON ARIAS",
            #                            position_dependency="TITULAR DE LA SECRETARÍA ANTICORRUPCIÓN Y BUEN GOBIERNO DEL ESTADO DE TABASCO.",
            #                            address="AV. PASEO TABASCO #1504",
            #                            colony="TABASCO 2000",
            #                            municipality="VILAHERMOSA",
            #                            state="TABASCO",
            #                            postal_code="86035",
            #                            number_volante="VCS-26-131000-00122",
            #                            contact="TEL. (444) 494 05 68",
            #                            instructions="ENTRE AVENIDA LUIS DONALDO COLOSIO Y PRIVADA",
            #                            ai_notes="SIN OBSERVACIONES",
            #                            crop_x=1, crop_y=1, crop_w=1, crop_h=1, rotation_deg=90,
            #                            aspect_mode="FREE",
            #                            created_by_user=user_new
            #                            )
            #
            # session.add_all([user_new, register_new])
            # session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(e)






