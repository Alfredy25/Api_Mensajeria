import pytest
from pydantic import ValidationError

from app.api.v1.receiver.schemas import ReceiverCreate
from app.models import EntidadesEnum


def base_address() -> dict:
    return {
        "street": "CALLE GUADALUPE VICTORIA",
        "num_street": "NUM. 312",
        "colony": "SALTILLO CENTRO",
        "municipality": "SALTILLO",
        "city": "SALTILLO",
        "state": "COAHUILA",
        "postal_code": "25000",
        "country": "Mexico",
    }

def base_title() -> dict:
    return {
        "abbreviation": "C.P.",
        "meaning": "Contador Público o Contadora Pública",
    }

def base_org() -> dict:
    return {
        "name": "AUDITORÍA GUBERNAMENTAL DE LA SECRETARÍA DE ANTICORRUPCIÓN Y BUEN GOBIERNO.",
        "state": "CAMPECHE",
    }

def base_job() -> dict:
    return {
        "abbreviation": "DIR.",
        "meaning": "Director",
    }

def base_position() -> dict:
    return {
            "job_role": base_job(),
            "organization": base_org(),
        }

def base_position_sin_job() -> dict:
    return {
        "organization": base_org(),
    }

def base_position_sin_organization() -> dict:
    """Position con cargo pero sin organización"""
    return {
        "job_role": base_job(),
    }

def base_volante() -> dict:
    return {
        "name": "VCS-26-131000-00167"
    }

def base_contact() -> dict:
    return {
        "phone":"8444160470",
        "ext": "111"
    }

def test_persona_minima_valida() -> None:
    """Persona minima válida con:
        - entidad PERSONA,
        - nombre completo,
        - email, -> Igual puede ser None
        - título,
        - dirección
        Sin referencia de domicilio,
        Sin un Puesto, que contiene cargo y dependencia,
        Sin Contacto,
        Sin Volante,
        """
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "BEATRÍZ ADRIANA CONTRERAS MARTINEZ",
        "email": "notificaciones@feuh.com.mx",
        "title": base_title(),
        "address": base_address(),
    }
    model = ReceiverCreate(**payload)
    print(model)
    assert model.type_entity == EntidadesEnum.PERSONA

def test_persona_con_full_name_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "ANA ", # Error no tiene apellidos
        "email": "notificaciones@feuh.com.mx",
        "title": base_title(),
        "address": base_address(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    assert errors[0].get('type') == "string_too_short"


def test_persona_con_organizacion_y_cargo_valido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "SERGIO CARLOS DE JESUS PÉREZ VÁZQUEZ.",
        "email": "notificaciones@feuh.com.mx",
        "title": base_title(),
        "address": base_address(),
        "position": base_position(),
        "volante": base_volante(),
        "contact": base_contact()
    }
    model = ReceiverCreate(**payload)
    print(f"\nPersona con organizacion y cargo valido\n{model}")
    assert model.type_entity == EntidadesEnum.PERSONA

def test_persona_con_organizacion_sin_cargo_valido() -> None:
     payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "SERGIO CARLOS DE JESUS PÉREZ VÁZQUEZ.",
        "email": "notificaciones@feuh.com.mx",
        "title": base_title(),
        "address": base_address(),
        "position": base_position_sin_job(),
    }
     model = ReceiverCreate(**payload)
     print(f"\nPersona con organizacion y sin cargo valido\n{model}")
     assert model.type_entity == EntidadesEnum.PERSONA

def test_persona_full_name_vacio_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "      ",
        "title": base_title(),
        "address": base_address(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    # print("\n", errors)
    assert errors[0].get('type') == "receiver_full_name_required_for_persona"

def test_persona_sin_titulo_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "BEATRÍZ ADRIANA CONTRERAS MARTINEZ",
        "email": "notificaciones@feuh.com.mx",
        "address": base_address(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    # print(f"\n{errors}")
    assert errors[0].get('type') == 'receiver_title_required_for_persona'

def test_gobierno_con_organizacion_y_sin_cargo_valido() -> None:
    payload = {
        "type_entity": EntidadesEnum.GOBIERNO,
        "address": base_address(),
        "position": base_position_sin_job(),
    }
    model = ReceiverCreate(**payload)
    print(f"\nGobierno con organizacion y sin cargo valido\n{model}")
    assert model.type_entity == EntidadesEnum.GOBIERNO

def test_privada_minima_valida() -> None:
    payload = {
        "type_entity": EntidadesEnum.PRIVADA,
        "address": base_address(),
        "position": base_position(),
    }
    model = ReceiverCreate(**payload)
    assert model.type_entity == EntidadesEnum.PRIVADA

def test_privada_con_organizacion_y_cargo_valido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PRIVADA,
        "address": base_address(),
        "position": base_position(),
        "volante": base_volante(),
        "contact": base_contact()
    }
    model = ReceiverCreate(**payload)
    print(f"\nGobierno con organizacion y cargo valido")
    assert model.type_entity == EntidadesEnum.PRIVADA

def test_gobierno_sin_position_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.GOBIERNO,
        "address": base_address(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    assert errors[0].get('type') == 'receiver_position_required'


def test_gobierno_con_nombre_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.GOBIERNO,
        "full_name": "ASF Auditoria",
        "address": base_address(),
        "position": base_position(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    assert errors[0].get('type') == 'receiver_name_title_forbidden_for_government_or_private'

def test_gobierno_con_titulo_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.GOBIERNO,
        "title": base_title(),
        "address": base_address(),
        "position": base_position(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    print(f"\n error gobierno con titulo invalido") # \n{errors}
    print(f"Mensaje: {errors[0].get('msg')}")
    assert errors[0].get('type') == "receiver_name_title_forbidden_for_government_or_private"


def test_cargo_sin_organizacion_invalido() -> None:
    payload = {
        "type_entity": EntidadesEnum.PERSONA,
        "full_name": "SERGIO CARLOS DE JESUS PÉREZ VÁZQUEZ.",
        "email": "notificaciones@feuh.com.mx",
        "title": base_title(),
        "address": base_address(),
        "position": base_position_sin_organization(),
    }
    with pytest.raises(ValidationError) as exc_info:
        ReceiverCreate(**payload)
    errors = exc_info.value.errors()
    print(f"\n error puesto con solo cargo sin organizacion") #\n{errors}
    print(f'Mensaje: {errors[0].get('msg')}')
    assert errors[0].get("loc") == ("position", "organization")
    assert errors[0].get("type") == "missing"