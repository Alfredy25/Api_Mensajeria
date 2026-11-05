import pytest
from fastapi.testclient import TestClient

from test.integration.conftest import SEED_NAMES

FOLIO_NUEVO = "VCS-26-131000-00170"
FOLIO_PATCH = "VCS-26-131000-00999"

@pytest.mark.integration
def test_given_seeded_volantes_when_list_requested_then_those_names_are_returned(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/")

    # Assert
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["items"]}
    assert names == set(SEED_NAMES)

@pytest.mark.integration
def test_given_seeded_folio_when_search_matches_suffix_then_only_that_volante_is_returned(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/", params={"search": "00167"})

    # Assert
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "VCS-26-131000-00167"

@pytest.mark.integration
def test_given_search_shorter_than_three_when_list_requested_then_unprocessable_entity(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/", params={"search": "AB"})

    # Assert
    assert response.status_code == 422

@pytest.mark.integration
def test_given_search_with_invalid_character_when_list_requested_then_unprocessable_entity(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/", params={"search": "VCS_26"})

    # Assert
    assert response.status_code == 422

@pytest.mark.integration
def test_given_page_zero_when_list_requested_then_unprocessable_entity(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/", params={"page": 0})

    # Assert
    assert response.status_code == 422

@pytest.mark.integration
def test_given_page_size_below_minimum_when_list_requested_then_unprocessable_entity(
    client: TestClient,
) -> None:
    # Act
    response = client.get("/volante/", params={"page_size": 4})

    # Assert
    assert response.status_code == 422

@pytest.mark.integration
def test_given_new_lowercase_name_when_volante_is_created_then_response_name_is_upper(
    client: TestClient,
) -> None:
    # Act
    created = client.post("/volante/", json={"name": FOLIO_NUEVO.lower()})
    listed = client.get("/volante/", params={"search": "00170"})

    # Assert
    assert created.status_code == 201
    assert created.json()["name"] == FOLIO_NUEVO
    assert listed.status_code == 200
    assert listed.json()["items"][0]["name"] == FOLIO_NUEVO

@pytest.mark.integration
def test_given_existing_folio_when_same_name_is_sent_lowercase_then_conflict(
    client: TestClient,
) -> None:
    # Act
    response = client.post("/volante/", json={"name": "vcs-26-131000-00167"})

    # Assert
    assert response.status_code == 409

@pytest.mark.integration
def test_given_existing_volante_when_name_is_patched_lowercase_then_response_name_is_upper(
    client: TestClient,
) -> None:
    # Arrange
    listed = client.get("/volante/", params={"search": "00167"})
    volante_id = listed.json()["items"][0]["id"]

    # Act
    response = client.patch(f"/volante/{volante_id}", json={"name": FOLIO_PATCH.lower()})

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == FOLIO_PATCH

@pytest.mark.integration
def test_given_missing_id_when_volante_is_patched_then_not_found(
    client: TestClient,
) -> None:
    # Act
    response = client.patch("/volante/999999", json={"name": FOLIO_PATCH})

    # Assert
    assert response.status_code == 404

@pytest.mark.integration
def test_given_id_below_one_when_volante_is_patched_then_unprocessable_entity(
    client: TestClient,
) -> None:
    # Act
    response = client.patch("/volante/0", json={"name": FOLIO_PATCH})

    # Assert
    assert response.status_code == 422
