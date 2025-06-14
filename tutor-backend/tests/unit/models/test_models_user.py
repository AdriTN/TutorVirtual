from sqlalchemy import Boolean, String, ColumnDefault
from sqlalchemy.orm.relationships import RelationshipProperty

from app.database.base import Base
# Importamos todos los módulos de modelos para que se registren en Base.metadata
import app.models.user          # noqa: F401
import app.models.course        # noqa: F401
import app.models.subject       # noqa: F401
import app.models.associations  # noqa: F401
import app.models.user_response # noqa: F401
import app.models.user_theme_progress  # noqa: F401

from app.models.user import User, UserProvider, RefreshToken


def test_users_table_registered():
    """La tabla 'users' debe estar en Base.metadata."""
    assert "users" in Base.metadata.tables


def test_users_columns_definition():
    """Comprueba columnas, tipos, PK, índices, uniques y defaults."""
    tbl = Base.metadata.tables["users"]
    assert [c.name for c in tbl.columns] == ["id", "username", "email", "password", "is_admin"]

    # id
    c = tbl.c.id
    assert c.primary_key is True
    assert c.nullable is False

    # username
    u = tbl.c.username
    assert isinstance(u.type, String)
    assert u.type.length == 120
    assert u.nullable is False

    # email
    e = tbl.c.email
    assert isinstance(e.type, String)
    assert e.type.length == 255
    assert e.nullable is False
    # la columna email es unique
    assert e.unique is True

    # password
    p = tbl.c.password
    assert isinstance(p.type, String)
    assert p.type.length == 100
    assert p.nullable is False

    # is_admin
    a = tbl.c.is_admin
    assert isinstance(a.type, Boolean)
    # default Python-level
    assert isinstance(a.default, ColumnDefault)
    assert a.default.arg is False
    # server_default SQL-level
    assert tbl.c.is_admin.server_default.arg in ("false", "FALSE")


def test_users_check_constraints():
    """Comprueba los CheckConstraint definidos en users."""
    tbl = Base.metadata.tables["users"]
    from sqlalchemy import CheckConstraint
    checks = [c for c in tbl.constraints if isinstance(c, CheckConstraint)]
    # Debe existir el constraint chk_username_minlen
    assert any(c.name == "chk_username_minlen" for c in checks)
    # Y su expresión debe contener 'length(username) >= 3'
    assert any("length(username) >= 3" in str(c.sqltext) for c in checks)


def test_user_relationships():
    """Verifica las relaciones ORM de User."""
    rels: dict[str, RelationshipProperty] = User.__mapper__.relationships

    # providers
    rp = rels["providers"]
    assert rp.mapper.class_ is UserProvider
    assert rp.back_populates == "user"
    assert rp.uselist is True

    # refresh_tokens
    rt = rels["refresh_tokens"]
    assert rt.mapper.class_ is RefreshToken
    assert rt.back_populates == "user"
    assert rt.uselist is True

    # respuestas (user_responses)
    rr = rels["respuestas"]
    from app.models.user_response import UserResponse
    assert rr.mapper.class_ is UserResponse
    assert rr.back_populates == "user"
    assert rr.uselist is True

    # progress (user_theme_progress)
    pg = rels["progress"]
    from app.models.user_theme_progress import UserThemeProgress
    assert pg.mapper.class_ is UserThemeProgress
    assert pg.uselist is True

    # courses (many-to-many)
    cr = rels["courses"]
    from app.models.course import Course
    assert cr.mapper.class_ is Course
    assert cr.secondary.name == "user_courses"
    assert cr.back_populates == "students"
    assert cr.uselist is True

    # subjects (many-to-many)
    sb = rels["subjects"]
    from app.models.subject import Subject
    assert sb.mapper.class_ is Subject
    assert sb.secondary.name == "user_subjects"
    assert sb.back_populates == "users"
    assert sb.uselist is True


def test_userprovider_table_and_columns():
    """Comprueba tabla y columnas de UserProvider."""
    tbl = Base.metadata.tables["users_providers"]
    assert [c.name for c in tbl.columns] == ["id", "user_id", "provider", "provider_user_id"]

    # id
    assert tbl.c.id.primary_key

    # user_id → ForeignKey(users.id)
    fk = list(tbl.c.user_id.foreign_keys)[0]
    assert fk.column.table.name == "users"
    assert fk.column.name == "id"

    # provider y provider_user_id
    from sqlalchemy import String
    prov = tbl.c.provider
    assert isinstance(prov.type, String) and prov.nullable is False
    puid = tbl.c.provider_user_id
    assert isinstance(puid.type, String) and puid.nullable is False

    # CheckConstraints
    from sqlalchemy import CheckConstraint
    checks = [c for c in tbl.constraints if isinstance(c, CheckConstraint)]
    names = {c.name for c in checks}
    assert names == {"chk_provider_uid", "chk_provider_name"}


def test_userprovider_relationship():
    """Verifica la relación back_populates en UserProvider."""
    rels = UserProvider.__mapper__.relationships
    urel = rels["user"]
    assert urel.mapper.class_ is User
    assert urel.back_populates == "providers"
    assert urel.uselist is False


def test_refreshtoken_table_and_columns():
    """Comprueba tabla y columnas de RefreshToken."""
    tbl = Base.metadata.tables["refresh_tokens"]
    assert [c.name for c in tbl.columns] == ["id", "user_id", "token", "expires_at", "created_at"]

    # id
    assert tbl.c.id.primary_key

    # user_id FK
    fk = list(tbl.c.user_id.foreign_keys)[0]
    assert fk.column.table.name == "users"
    assert fk.column.name == "id"

    # token unique + indexed
    tok = tbl.c.token
    assert tok.unique is True
    assert any(idx for idx in tbl.indexes if "token" in tuple(idx.columns.keys()))

    # expires_at
    from sqlalchemy import DateTime
    exp = tbl.c.expires_at
    assert isinstance(exp.type, DateTime)
    assert exp.nullable is False

    # created_at tiene server_default
    ca = tbl.c.created_at
    assert ca.server_default is not None


def test_refreshtoken_relationship():
    """Verifica la relación back_populates en RefreshToken."""
    rels = RefreshToken.__mapper__.relationships
    urel = rels["user"]
    assert urel.mapper.class_ is User
    assert urel.back_populates == "refresh_tokens"
    assert urel.uselist is False
