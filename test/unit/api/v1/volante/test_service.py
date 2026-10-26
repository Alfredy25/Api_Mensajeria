from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.volante.schemas import VolanteCreate, VolanteUpdate
from app.api.v1.volante.service import VolanteService
from app.models import VolanteORM

FOLIO = "VCS-26-131000-00167"
FOLIO_NUEVO = "VCS-26-131000-00170"


def _service() -> tuple[VolanteService, Mock, Mock]:
    db = Mock()
    repo = Mock()
    return VolanteService(db, repo), db, repo


def _volante(volante_id: int = 1, name: str = FOLIO) -> VolanteORM:
    return VolanteORM(id=volante_id, name=name)


def test_given_no_search_when_find_all_then_repository_receives_none() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 0, "total_pages": 0, "current_page": 1},
        [],
    )

    # Act
    service.find_all(None, 1, 50, "id", "asc")

    # Assert
    repo.list_all.assert_called_once_with(None, 1, 50, "id", "asc")


def test_given_padded_lowercase_search_when_find_all_then_repository_receives_upper_text() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 0, "total_pages": 0, "current_page": 1},
        [],
    )

    # Act
    service.find_all("  vcs-26 ", 1, 50, "id", "asc")

    # Assert
    assert repo.list_all.call_args.args[0] == "VCS-26"


def test_given_first_page_when_find_all_then_has_prev_is_false() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 60, "total_pages": 2, "current_page": 1},
        [],
    )

    # Act
    page = service.find_all(None, 1, 50, "id", "asc")

    # Assert
    assert page.has_prev is False


def test_given_more_pages_when_find_all_then_has_next_is_true() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 60, "total_pages": 2, "current_page": 1},
        [],
    )

    # Act
    page = service.find_all(None, 1, 50, "id", "asc")

    # Assert
    assert page.has_next is True


def test_given_no_rows_when_find_all_then_items_are_empty_and_flags_are_false() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 0, "total_pages": 0, "current_page": 1},
        [],
    )

    # Act
    page = service.find_all(None, 1, 50, "id", "asc")

    # Assert
    assert page.items == []
    assert page.has_prev is False
    assert page.has_next is False


def test_given_one_volante_when_find_all_then_item_is_a_dto() -> None:
    # Arrange
    service, _, repo = _service()
    repo.list_all.return_value = (
        {"total": 1, "total_pages": 1, "current_page": 1},
        [_volante()],
    )

    # Act
    page = service.find_all(None, 1, 50, "id", "asc")

    # Assert
    assert page.items[0].id == 1
    assert page.items[0].name == FOLIO


def test_given_existing_name_when_create_volante_then_conflict_and_no_commit() -> None:
    # Arrange
    service, db, repo = _service()
    repo.get_by_name.return_value = _volante()
    payload = VolanteCreate(name=FOLIO.lower())

    # Act
    with pytest.raises(HTTPException) as error:
        service.create_volante(payload)

    # Assert
    assert error.value.status_code == 409
    repo.get_by_name.assert_called_once_with(FOLIO)
    repo.create.assert_not_called()
    db.commit.assert_not_called()


def test_given_new_lowercase_name_when_create_volante_then_name_is_stored_upper() -> None:
    # Arrange
    service, db, repo = _service()
    repo.get_by_name.return_value = None
    repo.create.return_value = _volante(volante_id=4, name=FOLIO_NUEVO)
    payload = VolanteCreate(name=FOLIO_NUEVO.lower())

    # Act
    created = service.create_volante(payload)

    # Assert
    repo.create.assert_called_once_with(FOLIO_NUEVO)
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert created.name == FOLIO_NUEVO


def test_given_database_error_when_create_volante_then_session_rolls_back() -> None:
    # Arrange
    service, db, repo = _service()
    repo.get_by_name.return_value = None
    repo.create.side_effect = SQLAlchemyError("fallo")
    payload = VolanteCreate(name=FOLIO_NUEVO)

    # Act
    with pytest.raises(SQLAlchemyError):
        service.create_volante(payload)

    # Assert
    db.rollback.assert_called_once()


def test_given_missing_id_when_update_volante_then_not_found() -> None:
    # Arrange
    service, _, repo = _service()
    repo.find_by_id.return_value = None
    payload = VolanteUpdate(name=FOLIO_NUEVO)

    # Act
    with pytest.raises(HTTPException) as error:
        service.update_volante(9, payload)

    # Assert
    assert error.value.status_code == 404
    repo.update.assert_not_called()


def test_given_lowercase_name_when_update_volante_then_name_is_stored_upper() -> None:
    # Arrange
    service, db, repo = _service()
    current = _volante()
    repo.find_by_id.return_value = current
    repo.get_by_name.return_value = None

    def apply_update(volante: VolanteORM, updates: dict) -> VolanteORM:
        for field, value in updates.items():
            setattr(volante, field, value)
        return volante

    repo.update.side_effect = apply_update
    payload = VolanteUpdate(name=FOLIO_NUEVO.lower())

    # Act
    updated = service.update_volante(1, payload)

    # Assert
    assert repo.update.call_args.args[1]["name"] == FOLIO_NUEVO
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert updated.name == FOLIO_NUEVO


def test_given_database_error_when_update_volante_then_session_rolls_back() -> None:
    # Arrange
    service, db, repo = _service()
    repo.find_by_id.return_value = _volante()
    repo.get_by_name.return_value = None
    repo.update.side_effect = SQLAlchemyError("fallo")
    payload = VolanteUpdate(name=FOLIO_NUEVO)

    # Act
    with pytest.raises(SQLAlchemyError):
        service.update_volante(1, payload)

    # Assert
    db.rollback.assert_called_once()


def test_given_existing_volante_when_ensure_volante_then_create_is_not_called() -> None:
    # Arrange
    service, db, repo = _service()
    current = _volante()
    repo.get_by_name.return_value = current
    payload = VolanteCreate(name=FOLIO.lower())

    # Act
    found = service.ensure_volante(payload)

    # Assert
    assert found is current
    repo.get_by_name.assert_called_once_with(FOLIO)
    repo.create.assert_not_called()
    db.flush.assert_not_called()


def test_given_new_lowercase_name_when_ensure_volante_then_name_is_flushed_upper() -> None:
    # Arrange
    service, db, repo = _service()
    repo.get_by_name.return_value = None
    repo.create.return_value = _volante(volante_id=4, name=FOLIO_NUEVO)
    payload = VolanteCreate(name=FOLIO_NUEVO.lower())

    # Act
    created = service.ensure_volante(payload)

    # Assert
    repo.get_by_name.assert_called_once_with(FOLIO_NUEVO)
    repo.create.assert_called_once_with(FOLIO_NUEVO)
    db.flush.assert_called_once()
    db.commit.assert_not_called()
    assert created.name == FOLIO_NUEVO
