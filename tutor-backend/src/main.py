from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.api.dependencies.settings import get_settings
from .app.core.logging import setup_logging
from .app.api.routes import api_router
from .app.database.base import Base
from .app.database.session import engine

# ── 1. logging y BD ──────────────────────────────────────────
setup_logging()
Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(title=settings.api_title, version="1.0.0")

# ── 2. CORS ─────────────────────────────────────────────────
origins = [f"http://localhost:{settings.port}", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins     = origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── 3. Rutas ────────────────────────────────────────────────
app.include_router(api_router, prefix="/api")

@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}
