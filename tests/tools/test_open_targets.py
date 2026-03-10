import json
from pathlib import Path
import httpx
import pytest
import respx

from src.tools.open_targets import search_disease, get_disease_targets

FIXTURES = Path(__file__).parent.parent / "fixtures"
OT_URL = "https://api.platform.opentargets.org/api/v4/graphql"


@respx.mock
@pytest.mark.asyncio
async def test_search_disease():
    fixture = json.loads((FIXTURES / "open_targets_search.json").read_text())
    respx.post(OT_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        result = await search_disease(client, "Alzheimer disease")

    assert result is not None
    assert result["id"] == "EFO_0000249"
    assert result["name"] == "Alzheimer disease"


@respx.mock
@pytest.mark.asyncio
async def test_search_disease_not_found():
    respx.post(OT_URL).mock(return_value=httpx.Response(200, json={
        "data": {"search": {"hits": []}}
    }))

    async with httpx.AsyncClient() as client:
        result = await search_disease(client, "nonexistent disease xyz")

    assert result is None


@respx.mock
@pytest.mark.asyncio
async def test_get_disease_targets():
    fixture = json.loads((FIXTURES / "open_targets_associations.json").read_text())
    respx.post(OT_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        targets = await get_disease_targets(client, "EFO_0000249", top_n=10)

    assert len(targets) == 2
    assert targets[0]["gene_symbol"] == "APOE"
    assert targets[0]["ensembl_id"] == "ENSG00000130203"
    assert targets[0]["association_score"] == 0.85
    assert targets[1]["gene_symbol"] == "APP"
