from sqlalchemy import Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql import func

from app.database.base import Base
# Importamos los modelos relacionados para forzar el registro en Base.metadata
import app.models.exercise
import app.models.user
from app.models.user_response import UserResponse
from app.models.exercise import Exercise
from app.models.user import User


def test_user_response_table_registered():
    """La tabla 'user_responses' debe estar registrada en Base.metadata."""
    assert "user_responses" in Base.metadata.tables


def test_user_response_columns_definition():
    """Verifica nombres, tipos, nullabilidad, PKs, FKs y default de las columnas."""
    tbl = Base.metadata.tables["user_responses"]
    cols = list(tbl.columns)
    assert [c.name for c in cols] == [
        "id",
        "answer",
        "correct",
        "time_sec",
        "created_at",
        "exercise_id",
        "user_id",
    ]

    # id
    assert tbl.c.id.primary_key is True
    assert tbl.c.id.nullable is False

    # answer: Text, not null
    assert isinstance(tbl.c.answer.type, Text)
    assert tbl.c.answer.nullable is False

    # correct: Boolean, not null
    assert isinstance(tbl.c.correct.type, Boolean)
    assert tbl.c.correct.nullable is False

    # time_sec: Integer, nullable (Mapped[int|None])
    assert tbl.c.time_sec.nullable is True

    # created_at: DateTime(timezone=True), default server side
    assert isinstance(tbl.c.created_at.type, DateTime)
    # comprobar que tiene default server-side de tipo func.now()
    default = tbl.c.created_at.server_default
    assert default is not None
    assert "now" in str(default.arg)

    # exercise_id: FK → exercises.id, not nullable
    fk_ex = list(tbl.c.exercise_id.foreign_keys)[0]
    assert fk_ex.column.table.name == "exercises"
    assert fk_ex.column.name == "id"
    assert tbl.c.exercise_id.nullable is False

    # user_id: FK → users.id, not nullable
    fk_us = list(tbl.c.user_id.foreign_keys)[0]
    assert fk_us.column.table.name == "users"
    assert fk_us.column.name == "id"
    assert tbl.c.user_id.nullable is False


def test_user_response_unique_constraint():
    """Comprueba que exista UniqueConstraint sobre (user_id, exercise_id)."""
    tbl = Base.metadata.tables["user_responses"]
    uqs = [c for c in tbl.constraints if isinstance(c, UniqueConstraint)]
    assert len(uqs) == 1
    uq = uqs[0]
    # Las columnas de la constraint, en el orden que aparecen
    assert tuple(uq.columns.keys()) == ("user_id", "exercise_id")
    assert uq.name == "uq_user_exercise"


def test_user_response_relationships():
    """Verifica las relaciones ORM: exercise y user."""
    mapper = UserResponse.__mapper__
    rels: dict[str, RelationshipProperty] = mapper.relationships

    # 1) ejercicio
    assert "exercise" in rels
    r_ex = rels["exercise"]
    assert r_ex.mapper.class_ is Exercise
    assert r_ex.back_populates == "responses"
    assert r_ex.uselist is False

    # 2) usuario
    assert "user" in rels
    r_us = rels["user"]
    assert r_us.mapper.class_ is User
    assert r_us.back_populates == "respuestas"
    assert r_us.uselist is False
