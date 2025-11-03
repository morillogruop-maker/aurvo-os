"""Application configuration for the AURVO backend."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List
import os


@dataclass(frozen=True)
class ModuleDefinition:
    """Declarative definition for a core AURVO module."""

    slug: str
    title: str
    description: str


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the FastAPI backend."""

    data_dir: Path
    modules: Dict[str, ModuleDefinition]


DEFAULT_MODULES: Dict[str, ModuleDefinition] = {
    "santosecure": ModuleDefinition(
        slug="santosecure",
        title="SantoSecure",
        description=(
            "Servicios de seguridad cuántica y monitoreo continuo para los entornos "
            "inteligentes de Aurvo."
        ),
    ),
    "hoc-engine": ModuleDefinition(
        slug="hoc-engine",
        title="HOC Engine",
        description=(
            "Motor cognitivo que orquesta datos, IA y automatizaciones en los "
            "diferentes dominios del ecosistema."
        ),
    ),
    "aurvocloud": ModuleDefinition(
        slug="aurvocloud",
        title="AurvoCloud",
        description=(
            "Infraestructura modular distribuida que aloja servicios, pipelines de IA "
            "y experiencias inmersivas."
        ),
    ),
    "aurvoui": ModuleDefinition(
        slug="aurvoui",
        title="AurvoUI",
        description=(
            "Interfaz de usuario áurea para experiencias premium en dispositivos y "
            "vehículos conectados."
        ),
    ),
    "aurvo-vehicles": ModuleDefinition(
        slug="aurvo-vehicles",
        title="Aurvo Vehicles",
        description=(
            "Integración del ecosistema cognitivo dentro de plataformas de movilidad "
            "y vehículos inteligentes."
        ),
    ),
}


@lru_cache()
def get_settings() -> Settings:
    """Build a cached ``Settings`` instance."""

    base_dir = Path(os.getenv("AURVO_DATA_DIR", "data"))
    data_dir = base_dir if base_dir.is_absolute() else Path.cwd() / base_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    return Settings(data_dir=data_dir, modules=DEFAULT_MODULES)


def list_modules() -> List[ModuleDefinition]:
    """Return the configured module definitions."""

    settings = get_settings()
    return list(settings.modules.values())


def get_module(slug: str) -> ModuleDefinition:
    """Fetch a specific module configuration or raise a ``KeyError``."""

    settings = get_settings()
    try:
        return settings.modules[slug]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise KeyError(f"No existe el módulo '{slug}'.") from exc
