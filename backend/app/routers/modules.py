"""Module-related API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..services import modules as module_service
from ..schemas.module import InsightCreate, InsightResponse, ModuleDetail, ModuleSummary

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("/", response_model=list[ModuleSummary], summary="Listar módulos")
async def list_modules() -> list[ModuleSummary]:
    """Return every configured module with its record count."""

    summaries = module_service.list_module_summaries()
    return [ModuleSummary(**summary) for summary in summaries]


@router.get(
    "/{slug}",
    response_model=ModuleDetail,
    summary="Detalle de un módulo",
)
async def retrieve_module(slug: str) -> ModuleDetail:
    """Return metadata and the stored insights for a module."""

    try:
        module = module_service.get_module_detail(slug)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ModuleDetail(**module)


@router.post(
    "/{slug}/insights",
    response_model=InsightResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear o actualizar insight",
)
async def create_insight(slug: str, payload: InsightCreate) -> InsightResponse:
    """Insert or update a module insight."""

    try:
        record = module_service.upsert_insight(slug, payload.key, payload.value)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return InsightResponse(**record)
