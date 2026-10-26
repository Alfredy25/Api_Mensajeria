import pytest
from pydantic import ValidationError

from app.api.v1.volante.schemas import VolanteCreate, VolanteUpdate


@pytest.mark.parametrize("model", [VolanteCreate, VolanteUpdate])
@pytest.mark.parametrize("length", [18, 35])
def test_given_name_inside_limits_when_schema_is_built_then_name_is_accepted(
    model: type[VolanteCreate],
    length: int,
) -> None:
    # Arrange
    name = "A" * length

    # Act
    volante = model(name=name)

    # Assert
    assert volante.name == name


@pytest.mark.parametrize("model", [VolanteCreate, VolanteUpdate])
@pytest.mark.parametrize("length", [17, 36])
def test_given_name_outside_limits_when_schema_is_built_then_validation_error_is_raised(
    model: type[VolanteCreate],
    length: int,
) -> None:
    # Act / Assert
    with pytest.raises(ValidationError):
        model(name="A" * length)
