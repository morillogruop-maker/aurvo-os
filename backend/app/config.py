"""Application configuration for the AURVO backend."""
from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

try:  # Python 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    tomllib = None  # type: ignore[assignment]


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


class ModuleConfigurationError(RuntimeError):
    """Raised when the module configuration payload is invalid."""


def _normalise_module_payload(payload: object) -> Iterable[Mapping[str, object]]:
    """Coerce raw payloads (list/dict) into an iterable of mappings."""

    if payload is None:
        raise ModuleConfigurationError("La configuración de módulos no puede estar vacía.")

    if isinstance(payload, Mapping):
        # Allow top-level {"modules": [...]} or a single module mapping
        if "modules" in payload:
            inner = payload["modules"]
            if isinstance(inner, Iterable):
                return _normalise_module_payload(inner)
            raise ModuleConfigurationError(
                "La clave 'modules' debe contener una lista de módulos."
            )
        return [payload]

    if not isinstance(payload, Iterable) or isinstance(payload, (str, bytes)):
        raise ModuleConfigurationError(
            "La configuración de módulos debe ser una lista de objetos JSON/TOML."
        )

    modules: list[Mapping[str, object]] = []
    for item in payload:
        if not isinstance(item, Mapping):
            raise ModuleConfigurationError(
                "Cada módulo debe representarse como un objeto con claves slug/title/description."
            )
        modules.append(item)
    return modules


def _load_modules_from_file(path: Path) -> Iterable[Mapping[str, object]]:
    """Load module definitions from a JSON or TOML document."""

    resolved = path.expanduser()
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved

    if not resolved.exists():
        raise ModuleConfigurationError(
            f"No se encontró el archivo de módulos en '{resolved}'."
        )

    content = resolved.read_text(encoding="utf-8")
    suffix = resolved.suffix.lower()
    if suffix == ".json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ModuleConfigurationError("El archivo JSON de módulos es inválido.") from exc
    elif suffix == ".toml":
        if tomllib is None:  # pragma: no cover - fallback
            raise ModuleConfigurationError(
                "La lectura de archivos TOML requiere Python 3.11 o superior."
            )
        try:
            payload = tomllib.loads(content)
        except (tomllib.TOMLDecodeError, AttributeError) as exc:  # pragma: no cover
            raise ModuleConfigurationError("El archivo TOML de módulos es inválido.") from exc
    else:
        raise ModuleConfigurationError(
            "Formato de archivo no soportado. Usa JSON o TOML para definir los módulos."
        )

    return _normalise_module_payload(payload)


def _build_module_map(payload: Iterable[Mapping[str, object]]) -> Dict[str, ModuleDefinition]:
    """Transform a raw payload into module definitions keyed by slug."""

    modules: Dict[str, ModuleDefinition] = {}
    for index, raw in enumerate(payload, start=1):
        try:
            slug = str(raw["slug"]).strip()
            title = str(raw["title"]).strip()
            description = str(raw["description"]).strip()
        except KeyError as exc:
            missing = exc.args[0]
            raise ModuleConfigurationError(
                f"Falta la clave requerida '{missing}' en la definición de módulo #{index}."
            ) from exc

        if not slug:
            raise ModuleConfigurationError(
                f"El módulo #{index} debe tener un 'slug' no vacío."
            )
        if slug in modules:
            raise ModuleConfigurationError(
                f"El slug '{slug}' está duplicado en la configuración de módulos."
            )

        modules[slug] = ModuleDefinition(slug=slug, title=title, description=description)

    if not modules:
        raise ModuleConfigurationError(
            "La configuración de módulos debe incluir al menos un proyecto."
        )

    return modules


def _load_module_definitions() -> Dict[str, ModuleDefinition]:
    """Load module definitions from defaults or environment overrides."""

    modules_env = os.getenv("AURVO_MODULES")
    modules_file = os.getenv("AURVO_MODULES_FILE")

    if modules_env:
        try:
            payload = json.loads(modules_env)
        except json.JSONDecodeError as exc:
            raise ModuleConfigurationError(
                "La variable AURVO_MODULES contiene JSON inválido."
            ) from exc
        return _build_module_map(_normalise_module_payload(payload))

    if modules_file:
        return _build_module_map(_load_modules_from_file(Path(modules_file)))

    return DEFAULT_MODULES


@lru_cache()
def get_settings() -> Settings:
    """Build a cached ``Settings`` instance."""

    base_dir = Path(os.getenv("AURVO_DATA_DIR", "data")).expanduser()
    data_dir = base_dir if base_dir.is_absolute() else Path.cwd() / base_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    try:
        modules = _load_module_definitions()
    except ModuleConfigurationError as exc:
        raise RuntimeError(str(exc)) from exc

    return Settings(data_dir=data_dir, modules=modules)


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


def reset_settings_cache() -> None:
    """Clear the cached settings instance (primarily for testing)."""

    get_settings.cache_clear()
