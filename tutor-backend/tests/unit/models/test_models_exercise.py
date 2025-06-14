import pytest
from sqlalchemy import Text, String, DateTime, ForeignKey
from sqlalchemy.orm import RelationshipProperty

from app.database.base import Base
import app.models.theme            # registra Theme y su relación
import app.models.user_response   # registra UserResponse y su relación
import app.models.exercise        # registra Exercise

from app.models.exercise import Exercise
from app.models.theme import Theme
from app.models.user_response import UserResponse


def test_exercise_table_registered():
    """La tabla 'exercises' debe estar registrada en Base.metadata."""
    assert "exercises" in Base.metadata.tables


def test_exercise_columns_definition():
    """Comprueba nombres, tipos, nullabilidad, PKs y default de las columnas."""
    tbl = Base.metadata.tables["exercises"]
    cols = list(tbl.columns)
    expected = [
        "id",
        "statement",
        "type",
        "difficulty",
        "answer",
        "explanation",
        "created_at",
        "theme_id",
    ]
    assert [c.name for c in cols] == expected

    # id es PK y no nullable
    assert tbl.c.id.primary_key is True
    assert tbl.c.id.nullable is False

    # statement → Text, not null
    assert isinstance(tbl.c.statement.type, Text)
    assert tbl.c.statement.nullable is False

    # type → String(50), not null
    assert isinstance(tbl.c.type.type, String)
    assert tbl.c.type.type.length == 50
    assert tbl.c.type.nullable is False

    # difficulty → String(50), not null
    assert isinstance(tbl.c.difficulty.type, String)
    assert tbl.c.difficulty.type.length == 50
    assert tbl.c.difficulty.nullable is False

    # answer → Text, not null
    assert isinstance(tbl.c.answer.type, Text)
    assert tbl.c.answer.nullable is False

    # explanation → Text, nullable
    assert isinstance(tbl.c.explanation.type, Text)
    assert tbl.c.explanation.nullable is True

    # created_at → DateTime(timezone=True) con server_default
    ca = tbl.c.created_at
    assert isinstance(ca.type, DateTime)
    assert ca.type.timezone is True
    assert ca.server_default is not None

    # theme_id → FK a themes.id, not null
    tid = tbl.c.theme_id
    assert tid.nullable is False
    fks = list(tid.foreign_keys)
    assert len(fks) == 1
    fk = fks[0]
    assert fk.column.table.name == "themes"
    assert fk.column.name == "id"


def test_exercise_relationships():
    """Verifica las relaciones ORM: theme y responses."""
    mapper = Exercise.__mapper__
    rels: dict[str, RelationshipProperty] = mapper.relationships

    # Relación 'theme'
    assert "theme" in rels
    r_theme = rels["theme"]
    assert r_theme.mapper.class_ is Theme
    assert r_theme.back_populates == "exercises"
    assert r_theme.uselist is False

    # Relación 'responses'
    assert "responses" in rels
    r_resp = rels["responses"]
    assert r_resp.mapper.class_ is UserResponse
    assert r_resp.back_populates == "exercise"
    assert "delete-orphan" in r_resp.cascade
    assert r_resp.uselist is True
