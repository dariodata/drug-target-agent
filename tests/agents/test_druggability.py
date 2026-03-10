import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.agents.druggability import run_druggability_assessor
from src.models import DruggabilityProfile

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.asyncio
async def test_run_druggability_assessor():
    uniprot_fixture = json.loads((FIXTURES / "uniprot_search.json").read_text())
    chembl_target_fixture = json.loads((FIXTURES / "chembl_target.json").read_text())
    chembl_act_fixture = json.loads((FIXTURES / "chembl_activities.json").read_text())
    chembl_mol_fixture = json.loads((FIXTURES / "chembl_molecules.json").read_text())

    mock_client = AsyncMock()

    async def mock_get(url, **kwargs):
        resp = AsyncMock()
        resp.raise_for_status = lambda: None
        if "uniprot" in url:
            resp.json = lambda: uniprot_fixture
        elif "target.json" in url:
            resp.json = lambda: chembl_target_fixture
        elif "activity.json" in url:
            resp.json = lambda: chembl_act_fixture
        elif "molecule/set" in url:
            resp.json = lambda: chembl_mol_fixture
        resp.text = ""
        return resp

    mock_client.get = mock_get

    with patch("src.agents.druggability.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Moderate druggability. The protein is secreted with known structures and existing compounds."
        profile = await run_druggability_assessor(mock_client, "APOE")

    assert isinstance(profile, DruggabilityProfile)
    assert profile.gene_symbol == "APOE"
    assert profile.uniprot_accession == "P02649"
    assert profile.has_3d_structure is True
    assert profile.num_known_compounds == 2
    assert profile.max_phase_drug == 4
