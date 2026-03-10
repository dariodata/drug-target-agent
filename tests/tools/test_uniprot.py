import json
from pathlib import Path
import httpx
import pytest
import respx

from src.tools.uniprot import fetch_protein_info

FIXTURES = Path(__file__).parent.parent / "fixtures"
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_protein_info():
    fixture = json.loads((FIXTURES / "uniprot_search.json").read_text())
    respx.get(UNIPROT_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        result = await fetch_protein_info(client, "APOE")

    assert result is not None
    assert result["accession"] == "P02649"
    assert result["gene_symbol"] == "APOE"
    assert "Secreted" in result["subcellular_locations"]
    assert len(result["pdb_ids"]) == 2
    assert "1BZ4" in result["pdb_ids"]
    assert len(result["protein_families"]) > 0


@respx.mock
@pytest.mark.asyncio
async def test_fetch_protein_info_not_found():
    respx.get(UNIPROT_URL).mock(return_value=httpx.Response(200, json={"results": []}))

    async with httpx.AsyncClient() as client:
        result = await fetch_protein_info(client, "FAKEGENE999")

    assert result is None
