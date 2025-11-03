"""Service layer for module data access."""
from __future__ import annotations

from typing import List

from ..config import get_module, list_modules
from ..db import core


def list_module_summaries() -> List[dict]:
    """Return metadata and basic statistics for each module."""

    summaries = []
    for module in list_modules():
        with core.connect(module.slug) as connection:
            core.initialise_database(connection)
            count = connection.execute(
                f"SELECT COUNT(*) AS count FROM {core.DATABASE_TABLE}"
            ).fetchone()["count"]
        summaries.append(
            {
                "slug": module.slug,
                "title": module.title,
                "description": module.description,
                "records": count,
            }
        )
    return summaries


def get_module_detail(slug: str) -> dict:
    """Return the module metadata together with its insights."""

    module = get_module(slug)
    with core.connect(slug) as connection:
        rows = connection.execute(
            f"SELECT key, value, updated_at FROM {core.DATABASE_TABLE} ORDER BY key"
        ).fetchall()
    return {
        "slug": module.slug,
        "title": module.title,
        "description": module.description,
        "insights": [dict(row) for row in rows],
    }


def upsert_insight(slug: str, key: str, value: str) -> dict:
    """Create or update an insight for a module."""

    get_module(slug)  # ensure module exists
    with core.connect(slug) as connection:
        core.initialise_database(connection)
        connection.execute(
            f"""
            INSERT INTO {core.DATABASE_TABLE} (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=datetime('now')
            """,
            (key, value),
        )
        row = connection.execute(
            f"SELECT key, value, updated_at FROM {core.DATABASE_TABLE} WHERE key = ?",
            (key,),
        ).fetchone()
        connection.commit()
    return dict(row)
