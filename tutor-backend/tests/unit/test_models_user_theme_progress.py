from sqlalchemy import Integer, DateTime as SaDateTime
from sqlalchemy.sql.schema import ColumnDefault

from app.database.base import Base
# Importamos los modelos relacionados para que sus tablas queden registradas
import app.models.user  # noqa: F401
import app.models.theme  # noqa: F401
from app.models.user_theme_progress import UserThemeProgress


def test_table_registered():
    """La tabla 'user_theme_progress' debe estar en Base.metadata."""
    assert "user_theme_progress" in Base.metadata.tables


def test_columns_definition():
    """Comprueba columnas, tipos, PKs, FKs, defaults y nullabilidad."""
    tbl = Base.metadata.tables["user_theme_progress"]
    cols = [c.name for c in tbl.columns]
    assert cols == ["user_id", "theme_id", "completed", "correct", "updated_at"]

    # user_id
    c = tbl.c.user_id
    assert c.primary_key is True
    assert c.nullable is False
    fk = list(c.foreign_keys)[0]
    assert fk.column.table.name == "users"
    assert fk.column.name == "id"

    # theme_id
    c2 = tbl.c.theme_id
    assert c2.primary_key is True
    assert c2.nullable is False
    fk2 = list(c2.foreign_keys)[0]
    assert fk2.column.table.name == "themes"
    assert fk2.column.name == "id"

    # completed
    comp = tbl.c.completed
    assert isinstance(comp.type, Integer)
    assert comp.nullable is False
    # default Python-level
    assert isinstance(comp.default, ColumnDefault)
    assert comp.default.arg == 0

    # correct
    corr = tbl.c.correct
    assert isinstance(corr.type, Integer)
    assert corr.nullable is False
    assert isinstance(corr.default, ColumnDefault)
    assert corr.default.arg == 0

    # updated_at
    ut = tbl.c.updated_at
    assert isinstance(ut.type, SaDateTime)
    assert ut.type.timezone is True
    assert ut.nullable is False
    # default en BD
    sd = ut.server_default
    assert sd is not None
    assert "now" in str(sd.arg)
    # onupdate
    onup = ut.onupdate
    assert onup is not None
    assert "now" in str(onup.arg)
