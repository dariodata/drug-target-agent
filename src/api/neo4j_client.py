"""Neo4j async connection pool and query helpers."""

import os
from contextlib import asynccontextmanager

from neo4j import AsyncGraphDatabase


_driver = None


def get_driver():
    """Return the singleton async Neo4j driver."""
    global _driver
    if _driver is None:
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "")
        if not password:
            raise ValueError("NEO4J_PASSWORD environment variable is required")
        _driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    return _driver


async def close_driver():
    """Close the driver on shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


def set_driver(driver):
    """Override the driver (for testing)."""
    global _driver
    _driver = driver


async def query(cypher: str, **params) -> list[dict]:
    """Run a read query and return results as a list of dicts."""
    driver = get_driver()
    async with driver.session() as session:
        result = await session.run(cypher, **params)
        records = await result.data()
        return records


async def query_single(cypher: str, **params) -> dict | None:
    """Run a read query and return the first result or None."""
    results = await query(cypher, **params)
    return results[0] if results else None
