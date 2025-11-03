"""Tests for dynamic backend configuration."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import config


@pytest.fixture(autouse=True)
def reset_cache():
    """Ensure configuration cache is cleared before and after each test."""

    config.reset_settings_cache()
    yield
    config.reset_settings_cache()


def test_default_configuration(monkeypatch, tmp_path):
    """The defaults should be returned when no override is provided."""

    monkeypatch.delenv("AURVO_MODULES", raising=False)
    monkeypatch.delenv("AURVO_MODULES_FILE", raising=False)
    monkeypatch.setenv("AURVO_DATA_DIR", str(tmp_path))

    settings = config.get_settings()

    assert settings.data_dir == tmp_path
    assert set(settings.modules) == set(config.DEFAULT_MODULES)


def test_modules_override_via_env(monkeypatch, tmp_path):
    """Modules can be defined via the JSON payload environment variable."""

    payload = {
        "modules": [
            {
                "slug": "aurvo-ai",
                "title": "Aurvo AI",
                "description": "Laboratorio cognitivo.",
            }
        ]
    }

    monkeypatch.setenv("AURVO_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("AURVO_MODULES", json.dumps(payload))
    monkeypatch.delenv("AURVO_MODULES_FILE", raising=False)

    settings = config.get_settings()

    assert list(settings.modules) == ["aurvo-ai"]
    definition = settings.modules["aurvo-ai"]
    assert definition.title == "Aurvo AI"
    assert definition.description == "Laboratorio cognitivo."


def test_modules_override_via_file(monkeypatch, tmp_path):
    """Modules can be loaded from TOML or JSON files."""

    modules_file = tmp_path / "modules.toml"
    modules_file.write_text(
        """
[[modules]]
slug = "aurvo-iot"
title = "Aurvo IoT"
description = "Sensores distribuidos"
        """.strip()
    )

    monkeypatch.setenv("AURVO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AURVO_MODULES_FILE", str(modules_file))
    monkeypatch.delenv("AURVO_MODULES", raising=False)

    settings = config.get_settings()

    assert list(settings.modules) == ["aurvo-iot"]
    assert settings.modules["aurvo-iot"].title == "Aurvo IoT"
    assert settings.modules["aurvo-iot"].description == "Sensores distribuidos"
    assert settings.data_dir == (tmp_path / "data")


def test_invalid_module_payload_raises_runtime_error(monkeypatch, tmp_path):
    """Invalid module payloads surface as runtime errors with a friendly message."""

    monkeypatch.setenv("AURVO_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("AURVO_MODULES", "not-json")

    with pytest.raises(RuntimeError) as excinfo:
        config.get_settings()

    assert "JSON inválido" in str(excinfo.value)
