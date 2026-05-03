"""Smoke tests + one round-trip integration test for the MCP server."""
from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from src.mcp.server import (
    get_chembl_bioactivities,
    get_protein_info,
    get_reactome_pathways,
    mcp,
    search_pubmed_tool,
    search_targets,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"
OT_URL = "https://api.platform.opentargets.org/api/v4/graphql"


async def _registered_tool_names() -> set[str]:
    """Return the set of tool names registered on the FastMCP server."""
    return {t.name for t in await mcp.list_tools()}


@pytest.mark.asyncio
async def test_server_registers_alphafold_tool() -> None:
    assert "get_alphafold_structure" in await _registered_tool_names()


@pytest.mark.asyncio
async def test_server_registers_all_six_tools() -> None:
    expected = {
        "search_targets",
        "get_protein_info",
        "get_alphafold_structure",
        "get_chembl_bioactivities",
        "search_pubmed_tool",
        "get_reactome_pathways",
    }
    assert expected.issubset(await _registered_tool_names())


@pytest.mark.asyncio
async def test_server_tool_callables_match_registration() -> None:
    """Every imported tool callable should be registered by name on the server."""
    names = await _registered_tool_names()
    for fn in (
        search_targets,
        get_protein_info,
        get_chembl_bioactivities,
        search_pubmed_tool,
        get_reactome_pathways,
    ):
        assert fn.__name__ in names


@respx.mock
@pytest.mark.asyncio
async def test_search_targets_round_trip() -> None:
    """End-to-end: MCP search_targets resolves a disease then fetches its top targets."""
    search_fixture = json.loads((FIXTURES / "open_targets_search.json").read_text())
    assoc_fixture = json.loads((FIXTURES / "open_targets_associations.json").read_text())

    # Open Targets search and associations both POST to the same GraphQL URL.
    # respx returns the queued responses in the order they're requested.
    route = respx.post(OT_URL).mock(side_effect=[
        httpx.Response(200, json=search_fixture),
        httpx.Response(200, json=assoc_fixture),
    ])

    result = await search_targets("Alzheimer disease", top_n=5)

    assert route.call_count == 2
    assert result["disease"] == "Alzheimer disease"
    assert result["disease_id"] == "EFO_0000249"
    assert len(result["targets"]) == 2
    assert result["targets"][0]["gene_symbol"] == "APOE"


@respx.mock
@pytest.mark.asyncio
async def test_search_targets_returns_error_when_disease_unknown() -> None:
    respx.post(OT_URL).mock(return_value=httpx.Response(200, json={
        "data": {"search": {"hits": []}}
    }))

    result = await search_targets("nonexistent disease xyz")

    assert result == {"error": "disease_not_found", "disease": "nonexistent disease xyz"}
