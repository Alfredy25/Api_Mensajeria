from enum import StrEnum


class ReceiverErrorCode(StrEnum):
    FULL_NAME_REQUIRED_FOR_PERSONA = "receiver_full_name_required_for_persona" # Listo
    TITLE_REQUIRED_FOR_PERSONA = "receiver_title_required_for_persona" # Listo
    NAME_TITLE_FORBIDDEN_FOR_PRIVATE_OR_GOVERNMENT = "receiver_name_title_forbidden_for_government_or_private" # Listo
    POSITION_REQUIRED_FOR_PRIVATE_OR_GOVERNMENT = "receiver_position_required"