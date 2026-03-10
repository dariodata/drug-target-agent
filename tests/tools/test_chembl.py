import json
from pathlib import Path
import httpx
import pytest
import respx

from src.tools.chembl import (
    get_target_by_uniprot,
    get_activities,
    assess_compounds,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"
CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"


@respx.mock
@pytest.mark.asyncio
async def test_get_target_by_uniprot():
    fixture = json.loads((FIXTURES / "chembl_target.json").read_text())
    respx.get(f"{CHEMBL_BASE}/target.json").mock(
        return_value=httpx.Response(200, json=fixture)
    )

    async with httpx.AsyncClient() as client:
        result = await get_target_by_uniprot(client, "P02649")

    assert result is not None
    assert result["target_chembl_id"] == "CHEMBL2169736"


@respx.mock
@pytest.mark.asyncio
async def test_get_activities():
    fixture = json.loads((FIXTURES / "chembl_activities.json").read_text())
    respx.get(f"{CHEMBL_BASE}/activity.json").mock(
        return_value=httpx.Response(200, json=fixture)
    )

    async with httpx.AsyncClient() as client:
        activities = await get_activities(client, "CHEMBL2169736")

    assert len(activities) == 2
    assert activities[0]["molecule_chembl_id"] == "CHEMBL25"


@respx.mock
@pytest.mark.asyncio
async def test_assess_compounds():
    act_fixture = json.loads((FIXTURES / "chembl_activities.json").read_text())
    mol_fixture = json.loads((FIXTURES / "chembl_molecules.json").read_text())

    respx.get(f"{CHEMBL_BASE}/activity.json").mock(
        return_value=httpx.Response(200, json=act_fixture)
    )
    respx.get(url__startswith=f"{CHEMBL_BASE}/molecule/set/").mock(
        return_value=httpx.Response(200, json=mol_fixture)
    )

    async with httpx.AsyncClient() as client:
        result = await assess_compounds(client, "CHEMBL2169736")

    assert result["num_compounds"] == 2
    assert result["max_phase"] == 4
    assert result["top_compounds"][0]["pref_name"] == "ASPIRIN"
