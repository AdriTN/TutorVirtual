"""
conftest.py  –  configuración global de *pytest* para todo el proyecto.

Provee:

* BBDD SQLite en memoria reusable entre tests.
* TestClient con la app ya cableada a dicha BBDD y con autenticación
  simulada (``jwt_required`` siempre devuelve el mismo usuario admin).
* “Fake-psycopg” para que SQLAlchemy no requiera instalar la librería de
  PostgreSQL.
* Variables de entorno mínimas para que ``Settings`` valide.
* Reset de la caché de `Settings` y limpieza de la BBDD y del *logging*
  en cada test.
"""

from __future__ import annotations

# ───────────────────────────── stdlib ────────────────────────────────
import importlib
import logging
import os
import sys
import types
from pathlib import Path
from typing import Generator, Callable

# ───────────────────────────── terceros ──────────────────────────────
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ╭─────────────────────────── 1)  Fake-psycopg ─────────────────────────────╮
# │ SQLAlchemy carga el dialecto «postgresql+psycopg».                       │
# │ Para evitar instalar psycopg en el entorno de CI, inyectamos un módulo   │
# │ de mentira **antes** de que se produzca cualquier import.                │
# ╰───────────────────────────────────────────────────────────────────────────╯
def _fake_psycopg_module(name: str) -> types.ModuleType:
    m = types.ModuleType(name)
    m.paramstyle   = "pyformat"
    m.apilevel     = "2.0"
    m.__version__  = "3.1.0"
    m.adapters = {}

    # Árbol mínimo de sub-módulos que SQLAlchemy puede importar
    if name.endswith(".adapt"):
        class AdaptersMap(dict):
            """Placeholder para SQLAlchemy."""
            def __init__(self, adapters):
                super().__init__()
                self.adapters = adapters
                
        m.AdaptersMap = AdaptersMap

    # Jerarquía básica de excepciones
    class _BaseError(Exception): ...
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
    # Compatibilidad con proyectos que sigan usando «psycopg2»
    "psycopg2",
    "psycopg2.extensions",
):
    sys.modules.setdefault(_mod, _fake_psycopg_module(_mod))

# ──────────────────── 3) Añadimos el repo al PYTHONPATH ────────────────────
ROOT = Path(__file__).resolve().parents[1]  # …/tutor-backend
sys.path.insert(0, str(ROOT))               # para importar como «src.»

# ──────────────────────── 4) Importes de la app ────────────────────────────
from src.main import create_app
from src.app.database.base import Base
from src.app.database.session import get_db
from src.app.api.dependencies.auth import jwt_required
from src.app.api.dependencies import auth as auth_src

# Patch para que cada llamada a get_settings() cree nueva instancia
from src.app.core import config as _cfg


def _testing_get_settings() -> _cfg.Settings:  # type: ignore[return-value]
    """
    Sustituye a `get_settings` durante las pruebas:
    siempre devuelve una instancia fresca (sin caché).
    """
    return _cfg.Settings()  # lee las vars de entorno vigentes


_cfg.get_settings = _testing_get_settings  # type: ignore[assignment]
if hasattr(_cfg, "_settings"):
    delattr(_cfg, "_settings")            # elimina la caché, si había


# ╭────────────────────────── 5)  Fixtures de pytest ────────────────────────╮
# ╰───────────────────────────────────────────────────────────────────────────╯
# ------------------------- BBDD en memoria ---------------------------------
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
    """Sesión transaccional para cada test (rollback al salir)."""
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------- TestClient ------------------------------------
def _fake_user():
    return {"user_id": 1, "is_admin": True}

@pytest.fixture
def client(db_session: Session) -> TestClient:
    app = create_app()

    app.dependency_overrides[get_db] = lambda: db_session
    
    get_db_pkg = importlib.import_module("app.database.session").get_db
    app.dependency_overrides[get_db_pkg] = lambda: db_session

    app.dependency_overrides[auth_src.jwt_required]  = _fake_user
    app.dependency_overrides[auth_src.admin_required] = _fake_user

    # --- paquete app (el que usan los endpoints) ------------
    auth_pkg = importlib.import_module("app.api.dependencies.auth")
    app.dependency_overrides[auth_pkg.jwt_required]   = _fake_user
    app.dependency_overrides[auth_pkg.admin_required] = _fake_user

    return TestClient(app)


# -------------------- Reset del logger raíz entre tests --------------------
@pytest.fixture(autouse=True)
def reset_root_logger():
    logging.root.handlers.clear()
    logging.root.setLevel(logging.NOTSET)
    yield
    logging.root.handlers.clear()
    logging.root.setLevel(logging.NOTSET)


# ---------------------- Limpieza de la BBDD por test -----------------------
@pytest.fixture(autouse=True)
def _clean_db(db_session: Session):
    """Después de cada test borra todas las filas de todas las tablas."""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


# ----------------- Reset de Settings después de cada test ------------------
@pytest.fixture(autouse=True)
def _reset_settings_cache():
    """
    Antes de cada test limpiamos **toda** la caché de configuración
    para que Settings se vuelva a construir con las variables de entorno
    vigentes en ese instante.
    """
    from src.app.core import config as _cfg

    # 1. Si está decorado con lru_cache → vaciamos
    try:
        _cfg.get_settings.cache_clear()          # type: ignore[attr-defined]
    except AttributeError:
        pass

    # 2. Si el módulo mantiene un singleton manual (_settings, etc.)
    for attr in ("_settings", "settings", "SETTINGS"):
        if hasattr(_cfg, attr):
            delattr(_cfg, attr)

    yield

    # Repetimos al salir, por si el test construyó una nueva instancia
    try:
        _cfg.get_settings.cache_clear()          # type: ignore[attr-defined]
    except AttributeError:
        pass
    for attr in ("_settings", "settings", "SETTINGS"):
        if hasattr(_cfg, attr):
            delattr(_cfg, attr)
