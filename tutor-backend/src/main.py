"""
Punto de entrada FastAPI + application-factory.

> uvicorn src.main:create_app --factory --reload
"""
from pathlib import Path
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies.settings import get_settings
from src.core.logging      import setup_logging
from src.api.routes        import api_router
from src.database.base     import Base
from src.database.session  import get_engine


ROOT_DIR = Path(__file__).resolve().parents[2]
logger = structlog.get_logger(__name__)


# ────────────────────────────────────────────────────────────
def _configure_database(settings) -> None:
    """
    * **dev rápida**  ─ `AUTO_CREATE_TABLES=true`  → `Base.metadata.create_all`
    * **prod / CI**   ─ `RUN_MIGRATIONS=true`     → `alembic upgrade head`
    * **default**     ─ nada (asumes que ya existen las tablas)
    """
    engine = get_engine(settings.database_url, settings.pool_size)

    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
        return

    if settings.run_migrations_on_startup:
        from alembic import command
        from alembic.config import Config as AlembicConfig

        alembic_cfg = AlembicConfig(str(ROOT_DIR / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database_url))
        command.upgrade(alembic_cfg, "head")


def _configure_cors(app: FastAPI, settings) -> None:
    origins = [
        f"http://localhost:{settings.port}",
        "http://localhost:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins     = origins,
        allow_credentials = True,
        allow_methods     = ["*"],
        allow_headers     = ["*"],
    )


# ────────────────────────────────────────────────────────────
def create_app() -> FastAPI:            # ← exported factory
    setup_logging()
    logger.info("Logging configurado.")
    settings = get_settings()
    logger.info("Configuración cargada.", settings=settings)

    _configure_database(settings)
    logger.info("Base de datos configurada.")

    app = FastAPI(
        title   = settings.api_title,
        version = settings.api_version,
    )
    logger.info("Aplicación FastAPI creada.", title=settings.api_title, version=settings.api_version)

    _configure_cors(app, settings)
    logger.info("CORS configurado.")

    # Rutas ------------------------------------------------------------------
    app.include_router(api_router, prefix="/api")
    logger.info("Rutas de API incluidas con prefijo /api.")

    @app.get("/", tags=["health"])
    def health():
        logger.debug("Health check endpoint llamado.")
        return {"status": "ok"}

    logger.info("Aplicación creada y lista.")
    return app
