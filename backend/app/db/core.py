"""Database utilities for multi-database support."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

from ..config import ModuleDefinition, get_module, get_settings, list_modules

DATABASE_TABLE = "project_insights"


def get_database_path(module: ModuleDefinition) -> Path:
    """Return the on-disk path for a module database."""

    settings = get_settings()
    return settings.data_dir / f"{module.slug}.db"


@contextmanager
def connect(module_slug: str) -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields a SQLite connection for the given module."""

    module = get_module(module_slug)
    db_path = get_database_path(module)
    connection = sqlite3.connect(db_path)
    try:
        connection.row_factory = sqlite3.Row
        yield connection
    finally:
        connection.close()


def initialise_database(connection: sqlite3.Connection) -> None:
    """Ensure the core table exists for the provided connection."""

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {DATABASE_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    connection.commit()


def bootstrap_databases() -> None:
    """Create all configured databases if they are missing."""

    for module in list_modules():
        db_path = get_database_path(module)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as connection:
            initialise_database(connection)


def seed_records(
    module_slug: str,
    records: Iterable[tuple[str, str]],
) -> None:
    """Insert default records for a module database when missing."""

    with connect(module_slug) as connection:
        initialise_database(connection)
        for key, value in records:
            connection.execute(
                f"""
                INSERT INTO {DATABASE_TABLE} (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=datetime('now')
                """,
                (key, value),
            )
        connection.commit()
