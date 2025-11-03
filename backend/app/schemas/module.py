"""Pydantic models for module endpoints."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ModuleSummary(BaseModel):
    slug: str = Field(..., description="Identificador interno del módulo")
    title: str = Field(..., description="Nombre legible del módulo")
    description: str = Field(..., description="Descripción del dominio cognitivo")
    records: int = Field(..., description="Cantidad de insights registrados")


class Insight(BaseModel):
    key: str = Field(..., description="Clave única del insight")
    value: str = Field(..., description="Contenido del insight")
    updated_at: datetime = Field(..., description="Fecha de la última actualización")


class ModuleDetail(BaseModel):
    slug: str
    title: str
    description: str
    insights: list[Insight]


class InsightCreate(BaseModel):
    key: str = Field(..., description="Identificador del insight")
    value: str = Field(..., description="Información a registrar")


class InsightResponse(Insight):
    pass
