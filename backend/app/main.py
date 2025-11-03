"""FastAPI application entrypoint for the AURVO backend."""
from __future__ import annotations

from fastapi import FastAPI

from .config import get_settings
from .db.core import bootstrap_databases, seed_records
from .routers import health, modules

app = FastAPI(
    title="AURVO Backend",
    description="API modular para la hiperorquestación cognitiva de AURVO.",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialise module databases on application startup."""

    bootstrap_databases()
    settings = get_settings()
    for module in settings.modules.values():
        seed_records(
            module.slug,
            [
                ("descripcion", module.description),
                ("estado", "operativo"),
            ],
        )


app.include_router(health.router)
app.include_router(modules.router)


@app.get("/", tags=["root"], summary="Bienvenida")
async def root() -> dict:
    """Small welcome payload to help with service discovery."""

    return {
        "message": "Bienvenido a la API cognitiva de AURVO.",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
    }
