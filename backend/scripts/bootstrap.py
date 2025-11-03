"""Utility script to bootstrap local databases."""
from __future__ import annotations

from backend.app.config import get_settings
from backend.app.db.core import bootstrap_databases, seed_records


def main() -> None:
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
    print("Bases de datos inicializadas en", settings.data_dir)


if __name__ == "__main__":
    main()
