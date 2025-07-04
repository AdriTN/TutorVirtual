"""
Punto de entrada FastAPI + application-factory.

> uvicorn src.main:create_app --factory --reload
"""
from pathlib import Path
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from sqlalchemy.orm import Session

from sqlalchemy.orm import Session

from src.api.dependencies.settings import get_settings
from src.core.logging      import setup_logging
from src.core.security     import hash_password
from src.api.routes        import api_router
from src.database.base     import Base
from src.database.session  import SessionLocal, get_engine
from src.models.user       import User


APP_ROOT_DIR = Path(__file__).resolve().parents[1]
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

        alembic_ini_path = str(APP_ROOT_DIR / "alembic.ini")
        logger.info("Alembic ini path", path=alembic_ini_path)
        alembic_cfg = AlembicConfig(alembic_ini_path)
        alembic_cfg.config_file_name = alembic_ini_path
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database_url))
        
        logger.info("Alembic Config Inspection", 
                    file_name=alembic_cfg.config_file_name,
                    script_loc_main_opt=alembic_cfg.get_main_option("script_location"),
                    script_loc_attr=getattr(alembic_cfg, 'script_location', 'Not found as attr'),
                    attributes=getattr(alembic_cfg, 'attributes', {}) 
                   )
        try:
            if hasattr(alembic_cfg, 'file_config') and alembic_cfg.file_config:
                logger.info("Alembic INI Sections", sections=list(alembic_cfg.file_config.sections()))
                if alembic_cfg.file_config.has_section('alembic'):
                    logger.info("Alembic INI [alembic] section items", items=list(alembic_cfg.file_config.items('alembic')))
            else:
                logger.warn("alembic_cfg.file_config is not set or None")
        except Exception as e:
            logger.error("Error inspecting alembic_cfg.file_config", error=str(e))

        command.upgrade(alembic_cfg, "head")


def _create_admin_user(settings) -> None:
    if not all([settings.admin_email, settings.admin_username, settings.admin_password]):
        logger.info("Las variables de entorno del administrador no están configuradas, omitiendo la creación del usuario administrador.")
        return

    db: Session = SessionLocal()

    try:
        admin_user = db.query(User).filter(User.email == settings.admin_email).first()
        if admin_user:
            logger.info("El usuario administrador ya existe.", email=settings.admin_email)
        else:
            hashed_password = hash_password(settings.admin_password)
            new_admin_user = User(
                email=settings.admin_email,
                username=settings.admin_username,
                password=hashed_password,
                is_admin=True,
            )
            db.add(new_admin_user)
            db.commit()
            logger.info("Usuario administrador creado exitosamente.", username=settings.admin_username, email=settings.admin_email)
    except Exception as e:
        logger.error("Error al crear el usuario administrador.", error=str(e))
        db.rollback()
    finally:
        db.close()


def _configure_cors(app: FastAPI, settings) -> None:
    configured_origins = [str(url).rstrip('/') for url in settings.cors_origins]

    if configured_origins:
        allow_origins_list = configured_origins
    else:
        allow_origins_list = [
            "http://localhost:5173",
        ]


    app.add_middleware(
        CORSMiddleware,
        allow_origins     = allow_origins_list,
        allow_credentials = True,
        allow_methods     = ["*"],
        allow_headers     = ["*"],
    )


# ────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    setup_logging()
    logger.info("Logging configurado.")
    settings = get_settings()
    logger.info("Configuración cargada.", settings=settings)

    _configure_database(settings)
    logger.info("Base de datos configurada.")

    _create_admin_user(settings)

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
