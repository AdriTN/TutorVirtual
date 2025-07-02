"""
conftest.py – configuración global de *pytest*.

Provee:

* BBDD SQLite en memoria reusable entre tests.
* TestClient con la app ya cableada a dicha BBDD y con autenticación simulada.
* “Fake-psycopg” para que SQLAlchemy no requiera instalar psycopg.
* Variables de entorno mínimas para que Settings valide.
* Reset de la caché de Settings, de la BBDD y del logging en cada test.
"""

from __future__ import annotations

# ───────────────────────── stdlib ─────────────────────────
import importlib
import logging
import os
import sys
import types
from pathlib import Path
from typing import Generator

# ───────────────────────── terceros ───────────────────────
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ╭──────────── 1) Fake-psycopg ────────────────────────────╮
def _fake_psycopg_module(name: str) -> types.ModuleType:
    m = types.ModuleType(name)
    m.paramstyle = "pyformat"
    m.apilevel = "2.0"
    m.__version__ = "3.1.0"
    m.adapters = {}

    if name.endswith(".adapt"):

        class AdaptersMap(dict):
            ...

        m.AdaptersMap = AdaptersMap

    class _BaseError(Exception):
        ...

    m.Error = m.DatabaseError = m.OperationalError = _BaseError

    def _connect(*_, **__):
        raise RuntimeError("psycopg.connect() no debe usarse en tests")

    m.connect = _connect
    return m


for _mod in (
    "psycopg",
    "psycopg_pool",
    "psycopg.rows",
    "psycopg.adapt",
    "psycopg2",
    "psycopg2.extras",
):
    sys.modules.setdefault(_mod, _fake_psycopg_module(_mod))

# ───────────── 2) Añadimos repo a PYTHONPATH ──────────────
ROOT = Path(__file__).resolve().parents[1]  # …/tutor-backend
sys.path.insert(0, str(ROOT))               # para importar como «src.»

# ───────────── 3) Importes de la app ─────────────────────
from src.main import create_app
from src.database.base import Base
from src.database.session import get_db
from src.api.dependencies import auth as auth_src

# ───────────── 4) Vars de entorno mínimas ────────────────
@pytest.fixture(scope="session", autouse=True)
def _min_env_vars():
    os.environ.setdefault("DATABASE_URL", "sqlite://")
    os.environ.setdefault("JWT_SECRET", "x" * 32)
    os.environ.setdefault("OLLAMA_URL", "http://localhost")
    yield

# ───────────── 5) Engine SQLite memoria ──────────────────
@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


@pytest.fixture(scope="session", autouse=True)
def tables(engine):
    """Crea y destruye todas las tablas una sola vez por sesión."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """Sesión transaccional para cada test."""
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ───────────── 6) TestClient configurado ─────────────────
def _fake_user():
    return {"user_id": 1, "is_admin": True}


def _fake_non_admin_user():
    # Using user_id = 2 for non-admin to differentiate from the default admin (user_id=1)
    # Tests using this client might need to ensure user 2 exists in the DB.
    return {"user_id": 2, "is_admin": False}


@pytest.fixture
def client(db_session: Session) -> TestClient:
    app = create_app()

    # inyectamos la sesión SQLite
    app.dependency_overrides[get_db] = lambda: db_session
    # duplicado por si algunos endpoints importan get_db distinto
    importlib.import_module("src.database.session").get_db
    app.dependency_overrides[
        importlib.import_module("src.database.session").get_db
    ] = lambda: db_session

    # autenticación simulada para el cliente admin
    app.dependency_overrides[auth_src.jwt_required] = _fake_user
    app.dependency_overrides[auth_src.admin_required] = _fake_user

    return TestClient(app)


@pytest.fixture
def non_admin_client(db_session: Session) -> TestClient:
    app = create_app()

    # inyectamos la sesión SQLite
    app.dependency_overrides[get_db] = lambda: db_session
    importlib.import_module("src.database.session").get_db
    app.dependency_overrides[
        importlib.import_module("src.database.session").get_db
    ] = lambda: db_session

    # autenticación simulada para el cliente no-admin
    # admin_required should raise an exception if called by this client.
    # For jwt_required, it provides the non_admin user details.
    app.dependency_overrides[auth_src.jwt_required] = _fake_non_admin_user
    
    # For endpoints protected by admin_required, the actual admin_required dependency
    # should be used, which will then fail as _fake_non_admin_user returns is_admin=False.
    # No need to override admin_required to _fake_non_admin_user here, 
    # as that would incorrectly satisfy the admin check.

    return TestClient(app)

# ───────────── 7) Limpieza global por test ───────────────
@pytest.fixture(autouse=True)
def reset_root_logger():
    logging.root.handlers.clear()
    logging.root.setLevel(logging.NOTSET)
    yield
    logging.root.handlers.clear()
    logging.root.setLevel(logging.NOTSET)


@pytest.fixture(autouse=True)
def _clean_db(db_session: Session):
    """Después de cada test borra todas las filas de todas las tablas."""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

# ───────────── 8) Reset de Settings cache ────────────────
@pytest.fixture(autouse=True)
def _reset_settings_cache():
    """
    Antes y después de cada test limpiamos la caché de get_settings()
    para que lea las variables de entorno vigentes.
    """
    from src.core import config as _cfg

    try:
        _cfg.get_settings.cache_clear()  # type: ignore[attr-defined]
    except AttributeError:
        pass

    for attr in ("_settings", "settings", "SETTINGS"):
        if hasattr(_cfg, attr):
            delattr(_cfg, attr)

    yield

    try:
        _cfg.get_settings.cache_clear()  # type: ignore[attr-defined]
    except AttributeError:
        pass
    for attr in ("_settings", "settings", "SETTINGS"):
        if hasattr(_cfg, attr):
            delattr(_cfg, attr)
