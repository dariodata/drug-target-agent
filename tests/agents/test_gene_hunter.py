import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.agents.gene_hunter import run_gene_hunter
from src.models import GeneAssociation

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.asyncio
async def test_run_gene_hunter():
    search_fixture = json.loads((FIXTURES / "open_targets_search.json").read_text())
    assoc_fixture = json.loads((FIXTURES / "open_targets_associations.json").read_text())

    mock_client = AsyncMock()
    mock_response_search = AsyncMock()
    mock_response_search.raise_for_status = lambda: None
    mock_response_search.json = lambda: search_fixture

    mock_response_assoc = AsyncMock()
    mock_response_assoc.raise_for_status = lambda: None
    mock_response_assoc.json = lambda: assoc_fixture

    mock_client.post = AsyncMock(side_effect=[mock_response_search, mock_response_assoc])

    with patch("src.agents.gene_hunter.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "The results look sufficient. Proceeding with top 2 targets."
        genes = await run_gene_hunter(mock_client, "Alzheimer disease", top_n=10)

    assert len(genes) == 2
    assert isinstance(genes[0], GeneAssociation)
    assert genes[0].gene_symbol == "APOE"
    assert genes[1].gene_symbol == "APP"
