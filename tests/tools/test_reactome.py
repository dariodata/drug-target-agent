import json
from pathlib import Path
import httpx
import pytest
import respx

from src.tools.reactome import fetch_pathways

FIXTURES = Path(__file__).parent.parent / "fixtures"
REACTOME_URL = "https://reactome.org/ContentService/search/query"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_pathways():
    fixture = json.loads((FIXTURES / "reactome_search.json").read_text())
    respx.get(REACTOME_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        result = await fetch_pathways(client, "DRD2")

    assert len(result) == 3
    assert result[0]["reactome_id"] == "R-HSA-6794362"
    assert result[0]["name"] == "Protein-protein interactions at synapses"
    assert result[1]["reactome_id"] == "R-HSA-112316"
    assert result[2]["reactome_id"] == "R-HSA-500792"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_pathways_empty():
    respx.get(REACTOME_URL).mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    async with httpx.AsyncClient() as client:
        result = await fetch_pathways(client, "FAKEGENE999")

    assert result == []


@respx.mock
@pytest.mark.asyncio
async def test_fetch_pathways_deduplicates():
    """Duplicate stIds across groups should be deduplicated."""
    fixture = {
        "results": [
            {
                "typeName": "Pathway",
                "entries": [
                    {"stId": "R-HSA-123", "name": "Pathway A"},
                    {"stId": "R-HSA-456", "name": "Pathway B"},
                ],
            },
            {
                "typeName": "Pathway",
                "entries": [
                    {"stId": "R-HSA-123", "name": "Pathway A"},
                ],
            },
        ]
    }
    respx.get(REACTOME_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        result = await fetch_pathways(client, "HTT")

    assert len(result) == 2
