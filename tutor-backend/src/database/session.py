"""Gestión de la sesión de SQLAlchemy para FastAPI."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import get_settings

# ────────────────────────────────────────────────────────────────────────────────
# Configuración
# ────────────────────────────────────────────────────────────────────────────────
_settings = get_settings()

# from sqlalchemy import create_engine # No es necesaria aquí, ya está importada globalmente
# from ..core.config import get_settings # No es necesaria aquí, _settings ya está definido

# _settings = get_settings() # Redundante

def get_engine(db_url: str | None = None, pool_size: int | None = None):
    """
    Crea (o reutiliza) el motor de SQLAlchemy.

    Args:
        db_url: URL de la base de datos; por defecto la del .env.
        pool_size: Tamaño del pool; por defecto el configurado.

    Returns:
        sqlalchemy.Engine
    """
    url  = str(db_url or _settings.database_url)
    size = pool_size or _settings.pool_size
    return create_engine(url, pool_size=size, echo=False, future=True)


SessionLocal = sessionmaker(
    bind=get_engine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ────────────────────────────────────────────────────────────────────────────────
# Dependencia para FastAPI
# ────────────────────────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """Crea una sesión por petición y la cierra al final."""
    db: Session = SessionLocal()
    try:
        yield db          # ← FastAPI inyecta aquí la sesión real
        db.commit()       # Opcional: comenta si prefieres commits explícitos
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
