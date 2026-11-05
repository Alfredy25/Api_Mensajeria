from sqlalchemy import select
from sqlalchemy.dialects import sqlite

from app.api.v1.volante.repository import VolanteRepositoryImpl
from app.models import VolanteORM


def _order_sql(order_by: str, direction: str) -> str:
    statement = VolanteRepositoryImpl._apply_order(
        order_by,
        direction,
        select(VolanteORM),
    )
    return str(statement.compile(dialect=sqlite.dialect()))


def test_given_no_rows_when_totals_calculated_then_page_is_one_and_offset_is_zero() -> None:
    # Act
    total_pages, current_page, offset = VolanteRepositoryImpl._calculate_totals(0, 50, 10)

    # Assert
    assert total_pages == 0
    assert current_page == 1
    assert offset == 0


def test_given_page_past_the_end_when_totals_calculated_then_last_page_is_used() -> None:
    # Act
    total_pages, current_page, offset = VolanteRepositoryImpl._calculate_totals(120, 50, 10)

    # Assert
    assert total_pages == 3
    assert current_page == 3
    assert offset == 100


def test_given_page_inside_range_when_totals_calculated_then_offset_matches_that_page() -> None:
    # Act
    total_pages, current_page, offset = VolanteRepositoryImpl._calculate_totals(120, 50, 2)

    # Assert
    assert total_pages == 3
    assert current_page == 2
    assert offset == 50


def test_given_name_and_asc_when_order_applied_then_statement_orders_by_name_asc() -> None:
    # Act
    sql = _order_sql("name", "asc")

    # Assert
    assert "volantes.name ASC" in sql


def test_given_name_and_desc_when_order_applied_then_statement_orders_by_name_desc() -> None:
    # Act
    sql = _order_sql("name", "desc")

    # Assert
    assert "volantes.name DESC" in sql


def test_given_unknown_field_when_order_applied_then_statement_orders_by_id() -> None:
    # Act
    sql = _order_sql("otro", "asc")

    # Assert
    assert "volantes.id ASC" in sql
