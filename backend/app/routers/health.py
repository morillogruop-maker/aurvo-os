"""Health check endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from ..services import modules as module_service

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado del backend")
async def healthcheck() -> dict:
    """Return a minimal status payload for uptime monitors."""

    summaries = module_service.list_module_summaries()
    return {"status": "ok", "modules": summaries}
