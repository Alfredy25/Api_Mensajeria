from enum import StrEnum
from typing import Annotated, List, Literal, Optional
import re
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

# La Ñ se conserva porque es una letra, no un acento.
_VOWEL_ACCENTS = str.maketrans({
    "Á": "A",
    "É": "E",
    "Í": "I",
    "Ó": "O",
    "Ú": "U",
    "Ü": "U",
})

STREET_ABBREVIATIONS = {
    "CALLE": "C.",
    "AVENIDA": "AV.",
    "AV": "AV.",
    "BOULEVARD": "BLVD.",
    "CARRETERA": "CARR.",
    "SIN NÚMERO": "SN.",
    "SIN NUMERO": "SN.",
    "S/N": "SN",
    "NUMERO": "NUM.",
    "NÚMERO": "NUM.",
    "EDIFICIO": "EDIF.",
    "KILOMETRO": "KM.",
    "KM": "KM."
}

special_characters = {
    "\\": "",
    ":": "",
    "[": "",
    "]": "",
    "#": "",
    "°": "",
    "-": " ",
    '"': "",
    ",": "",
    "!": "",
    "¿": "",
    "¡": "",
    "“": "",
    "”": "",
}

def replace_special_characters(text: str) -> str:
    for key, value in special_characters.items():
        text = text.replace(key, value)
    return text

def normalize_text(value: str) -> str:
    return value.strip().upper().translate(_VOWEL_ACCENTS)

def normalize_text_fields(value: str | None) -> str:
    return value.strip().upper()

def replace_whole_words(value: str) -> str:
    words = sorted(
        STREET_ABBREVIATIONS,
        key=len,
        reverse=True,
    )

    regex = r"\b(?:{})\b".format(
        "|".join(
            re.escape(word)
            for word in words
        )
    )

    pattern = re.compile(regex)

    text = pattern.sub(
        lambda match: STREET_ABBREVIATIONS[match.group(0)],
        value
    )

    return replace_special_characters(text)

def normalize_state(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    return value


class MexicanState(StrEnum):
    AGUASCALIENTES = "AGUASCALIENTES"
    BAJA_CALIFORNIA = "BAJA CALIFORNIA"
    BAJA_CALIFORNIA_SUR = "BAJA CALIFORNIA SUR"
    CAMPECHE = "CAMPECHE"
    CHIAPAS = "CHIAPAS"
    CHIHUAHUA = "CHIHUAHUA"
    CIUDAD_DE_MEXICO = "CIUDAD DE MEXICO"
    COAHUILA = "COAHUILA"
    COLIMA = "COLIMA"
    DURANGO = "DURANGO"
    ESTADO_DE_MEXICO = "ESTADO DE MEXICO"
    GUANAJUATO = "GUANAJUATO"
    GUERRERO = "GUERRERO"
    HIDALGO = "HIDALGO"
    JALISCO = "JALISCO"
    MICHOACAN = "MICHOACAN"
    MORELOS = "MORELOS"
    NAYARIT = "NAYARIT"
    NUEVO_LEON = "NUEVO LEON"
    OAXACA = "OAXACA"
    PUEBLA = "PUEBLA"
    QUERETARO = "QUERETARO"
    QUINTANA_ROO = "QUINTANA ROO"
    SAN_LUIS_POTOSI = "SAN LUIS POTOSI"
    SINALOA = "SINALOA"
    SONORA = "SONORA"
    TABASCO = "TABASCO"
    TAMAULIPAS = "TAMAULIPAS"
    TLAXCALA = "TLAXCALA"
    VERACRUZ = "VERACRUZ"
    YUCATAN = "YUCATAN"
    ZACATECAS = "ZACATECAS"


MexicanStateField = Annotated[
    MexicanState,
    BeforeValidator(normalize_state),
]


class AddressUpdate(BaseModel):
    street: Optional[str] = Field(default=None, min_length=3, max_length=80)
    num_street: Optional[str] = Field(default=None, min_length=1, max_length=15)
    colony: Optional[str] = Field(default=None, min_length=3, max_length=60)
    municipality: Optional[str] = Field(default=None, min_length=3, max_length=60)
    city: Optional[str] = Field(default=None, min_length=3, max_length=60)
    state: Optional[MexicanStateField] = None
    postal_code: Optional[str] = Field(default=None, min_length=4, max_length=5)
    country: Optional[str] = Field(default=None, min_length=3, max_length=50)
    address_reference: Optional[str] = Field(default=None, max_length=50)

    @field_validator(
        "colony",
        "municipality",
        "city",
        "postal_code",
        "country",
        "address_reference",
        mode="before",
    )
    @classmethod
    def normalize_fields(cls, value: str) -> str | None:
        if value is None:
            return None

        return normalize_text_fields(value)


    @field_validator(
        "street",
        "num_street",
        mode="before",
    )
    @classmethod
    def normalize_address(cls, value):
        value = normalize_text_fields(value)
        return replace_whole_words(value)


class AddressCreate(BaseModel):
    street: str = Field(..., min_length=3, max_length=80)
    num_street: str = Field(..., min_length=1, max_length=15)
    colony: str = Field(..., min_length=3, max_length=60)
    municipality: str = Field(..., min_length=3, max_length=60)
    city: str = Field(..., min_length=3, max_length=60)
    state: MexicanStateField = Field(
        ...,
        description="Estado de la republica mexicana",
        examples=["JALISCO"],
    )
    postal_code: str = Field(..., min_length=4, max_length=5)
    country: str = Field(..., min_length=3, max_length=50)
    address_reference: Optional[str] = Field(default=None, max_length=50)

    @field_validator(
        "colony",
        "municipality",
        "city",
        "postal_code",
        "country",
        "address_reference",
        mode="before",
    )
    @classmethod
    def normalize_fields(cls, value: str) -> str | None:
        if value is None:
            return None

        return normalize_text_fields(value)

    @field_validator(
        "street",
        "num_street",
        mode="before",
    )
    @classmethod
    def normalize_address(cls, value) -> str | None:
        if value is None:
            return None
        value = normalize_text_fields(value)
        return replace_whole_words(value)


class AddressDto(BaseModel):
    id: int
    street: str
    num_street: str
    colony: str
    municipality: str
    city: str
    state: MexicanStateField = Field(
        ...,
        description="Estado de la republica mexicana",
        examples=["JALISCO"],
    )
    postal_code: str = Field(..., min_length=4, max_length=5)
    country: str
    address_reference: Optional[str] = Field(default=None, max_length=50)
    receiver_id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedAddresses(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "state"]
    direction: Literal["desc", "asc"]
    search: Optional[str] = None
    state: Optional[MexicanState] = None
    items: List[AddressDto] = Field(default_factory=list)


class TotalsAddresses(BaseModel):
    total: int
    total_pages: int
    current_page: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
